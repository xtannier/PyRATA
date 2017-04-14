# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Nicolas Hernandez 2017
# 
# The current parser is used to evaluate the semantic of a given pattern step
# 
# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import ply.yacc as yacc
from pyrata.lexer import *
from pyrata.semantic_step_parser import *
import pyrata.syntactic_analysis


# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class Match(object):

  groups = []          # list of triplet (value, start, end) e.g. [[0, 1, [{'pos': 'JJ', 'raw': 'fast'}]]]
  DEFAULT_GROUP_ID = 0
  (VALUE, START, END) = (0,1,2)

  def __init__(self, **kwargs):
    self.groups = []
    value = ''
    start = -1
    end = -1
    if 'start' in kwargs.keys(): # MANDATORY
      start = kwargs['start']
    if 'end' in kwargs.keys(): # MANDATORY
      end = kwargs['end']
    if 'value' in kwargs.keys(): # MANDATORY
      value = kwargs['value']
    if 'groups' in kwargs.keys(): # MANDATORY
      self.groups = kwargs['groups']  
      #print ('Debug: groups=', self.groups)
      #print ('Debug: Match__init__:(start={}, end={}, value={})'.format(startPosition, endPosition, value))
    else:  
      self.groups.append([value, start, end])
    #if  self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.VALUE] == '' or self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.START] == -1 or self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.END] == -1:   
    #  raise Exception('pyrata.re - attempt to create a Match object with incomplete informations')
    #print ('Debug: groups=', self.groups)

  def __repr__(self):
    return '<pyrata.re Match object; span=('+str(self.start())+', '+str(self.end())+'), match="'+str(self.group())+'">'

  def get_group_id(self, *argv):
    if len(argv) > 0:
      group_id = argv[0]
      if group_id > len(self.groups):
        raise IndexError ('In Match - group() function - wrong index required')
    else:
      group_id = Match.DEFAULT_GROUP_ID
    return group_id

  def group(self, *argv):
    ''' 
    Returns the corresponding value of one subgroup of the match. 
    Default is 0. The whole match value.
    '''
    return self.groups[self.get_group_id(*argv)][Match.VALUE]

  def groups (self):
    '''Return a tuple containing all the subgroups of the match, from 0. 
    In python re it is from 1 up to however many groups are in the pattern. '''
    return self.groups
    # if len(self.groups) > 0:
    #   return self.groups[1:len(self.groups)]   
    # else:
    #   return [] 

  def start(self, *argv):
    '''
    Return the indices of the start of the subdata matched by group; 
    group default to zero (meaning the whole matched data).
    '''
    return self.groups[self.get_group_id(*argv)][Match.START]

  def end(self, *argv):
    '''
    Return the indices of the end of the subdata matched by group; 
    group default to zero (meaning the whole matched data).
    '''
    return self.groups[self.get_group_id(*argv)][Match.END]

  def __eq__(self, other):
    if other == None: 
      return False
    if self.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.VALUE] == other.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.VALUE] and self.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.START] == other.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.START] and self.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.END] == other.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.END]:
      return True
      return True
    return False  
   
  def __ne__(self, other):
    if other == None: 
      return True   
    if self.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.VALUE] == other.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.VALUE] and self.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.START] == other.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.START] and self.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.END] == other.groups[self.get_group_id(Match.DEFAULT_GROUP_ID)][Match.END]:
      return False
    return True  

  #def __len__(self):
  #  return len(self.matcheslist)    

# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MatchesList(object):

  current = 0
  matcheslist = []

  def __init__(self, **kwargs):
    self.matcheslist = []

  def append(self, match):
    self.matcheslist.append(match)

  def group(self, *args):
    if len(self.matcheslist) == 0: 
      return None
    else:  
      if len(args) >0:
        if args[0] <0 and args[0] > len(self.matcheslist):
          raise Exception('Invalid group value out of range')
        return self.matcheslist[args[0]]
    return self.matcheslist[0]

  def start(self, *args):
    return self.group(*args).start()

  def end(self, *args):
    return self.group(*args).end()

  def __iter__(self):
    return iter(self.matcheslist)

  def next(self): # Python 3: def __next__(self)
    if self.current > len(self.matcheslist):
      raise StopIteration
    else:
      self.current += 1
    return self.matcheslist[self.current - 1]   

  def __len__(self):
    return len(self.matcheslist)

  # def __repr__(self):
  #   ml = ''
  #   for m in self.matcheslist:
  #     ml = ml + '<pyrata.re Match object; span=({}, {}), match="{}">\n'.format(str(m.start()), str(m.end()), str(m.group()))
  #   return ml

  def __eq__(self, other):
    if other == None: 
      return False       
    matches = 0
    for s, o in zip(self.matcheslist, other.matcheslist):
      if s == o: matches += 1
    if matches == len(self.matcheslist): 
      return True
    return False  

  def __ne__(self, other):
    if other == None: 
      return True       
    matches = 0
    for s, o in zip(self.matcheslist, other.matcheslist):
      if s == o: matches += 1
    if matches == len(self.matcheslist): 
      return False
    return True 

  def __repr__(self):
    return '<pyrata.re MatchesList object; matcheslist="'+str(self.matcheslist)+'">'


# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def evaluate (lexer, pattern_steps, pattern_cursor, data, data_cursor, **kwargs):
  '''
  Return a truth value which is True if the pattern_step recognizes the data_token
  '''

  quantifier, pattern_step = pattern_steps[pattern_cursor]

  verbosity = 0
  if 'verbosity' in kwargs.keys():
    verbosity = kwargs['verbosity']
  if verbosity >2:
    print ('\t_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _')

  data_cursor_extension  = 1
  group_id = 0

  if not(isinstance(pattern_step, list)): 
    if verbosity >2:
      print ('\tStarting the evaluation... of a pattern step single group=', pattern_step)

    lexer.lexer.data = [data[data_cursor]]
    lexer.lexer.data_cursor = 0
    lexer.lexer.pattern_cursor = 0
    e = SemanticStepParser(tokens=lexer.tokens, **kwargs)
    e.parser.parse(pattern_step, lexer.lexer) # removed tracking=True
  else:
    if verbosity >2:
      print ('\tStarting the evaluation... of a pattern step made of alternative groups=')
      print ('\t\t[')
      for g in pattern_step:
        print ('\t\t\t{}'.format(g))
      print ('\t\t]')
    #print ('Debug: lexer.group_pattern_offsets_group_list=',lexer.lexer.group_pattern_offsets_group_list)
    #local_l = lexer l # defines a new reference
    local_l = Lexer(pattern="", lexicons=lexer.lexer.lexicons)
    #print ('Debug: lexer.group_pattern_offsets_group_list=',lexer.lexer.group_pattern_offsets_group_list)
    #print ('Debug: local_l.group_pattern_offsets_group_list=',local_l.lexer.group_pattern_offsets_group_list)
    

    r = MatchesList()
    # while no match with a group and there is still at least a group to test
    #   add the must start constraint 
    #   then check
    while len(r) == 0 and group_id < len (pattern_step):
      if verbosity >2:
        print ('\tSemantic parsing initialization of pattern_steps_group[{}]={}'.format(group_id, pattern_step[group_id]))

      local_l.lexTokenEndDict = lexer.lexTokenEndDict

      local_l.lexTokenList = lexer.lexTokenList  # list of LexToken (self.type, self.value, self.lineno, self.lexpos)

      local_l.lexer.data = data 
      #local_l.lexer.pattern_data_start = 0      # position in the data from where the pattern is applied 
      #local_l.lexer.pattern_cursor = 0          # cursor to follow the parsing progress in the pattern
      local_l.lexer.pattern_steps =  pattern_step[group_id]         # compiled pattern: list of (quantifier=[None, '*', '+', '?'] not=[True, False] group=[True, False], step or group)
      local_l.lexer.pattern_must_match_data_start = True  # ^ matches the start of data before the first token in a data.
      #local_l.lexer.pattern_must_match_data_end = False    # $ matches the end of data ~after the last token of data.
      local_l.lexer.data_cursor = local_l.lexer.pattern_data_start     # position in the data that is explored by the current pattern
      #local_l.lexer.truth_value = False  # parsing result of a given pattern over a certain data 
      #local_l.lexer.quantified_step_index = 0     # syntactic pattern : parser quantified step index 
      #local_l.lexer.quantified_step_start = {}    # syntactic pattern parser : at a given position returns the quantified step index
      #local_l.lexer.quantified_step_end = {}      # syntactic pattern parser : at a given position returns the quantified step index
      #local_l.lexer.last_group_offsets_candidate = []     # last couple of index position of the current group
      local_l.lexer.group_pattern_offsets_group_list = [[0, len(pattern_step[group_id])]]    # list of group offsets e.g. [[start_i, end_i], [start_j, end_j], [start_k, end_k]]
      #local_l.lexer.step_already_counted = 0 # to prevent from duplicate step counting (wo then wi parenthesis) 
      #local_l.lexer.step_group_class = []    # step_group_class list of alternatives
      #print ('Debug: l.lexer.group_pattern_offsets_group_list=',local_l.lexer.group_pattern_offsets_group_list)
      local_cp = pyrata.syntactic_analysis.CompiledPattern(lexer=local_l, **kwargs)
      #print ('Debug: lexer.group_pattern_offsets_group_list=',lexer.lexer.group_pattern_offsets_group_list)
      #print ('Debug: local_l.group_pattern_offsets_group_list=',local_l.lexer.group_pattern_offsets_group_list)

      r = pyrata.semantic_analysis.parse_semantic (local_cp, data[data_cursor:], **kwargs)
      #print ('Debug: current pattern_steps={} i={} len (list of pattern_steps)={} '.format(local_l.lexer.pattern_steps, i, len (pattern_step)))

      group_id += 1

    if len(r) != 0:
      #len(pattern_step[i])
      # add a group 
      #len(r) FIXME indicate somehow the new data_cursor
      lexer.lexer.truth_value = True
      data_cursor_extension += len(r.group(0).group(0)) -1
      # modify the lexer
      #print ('Debug: lexer.group_pattern_offsets_group_list=',lexer.lexer.group_pattern_offsets_group_list)
      #print ('Debug: local_l.group_pattern_offsets_group_list=',local_l.lexer.group_pattern_offsets_group_list)
      #print ('Debug: r={}'.format(r))
      #print ('Debug: r[0][0]={}'.format(r.group(0).group(0)))
      #print ('Debug: data_cursor_extension=',data_cursor_extension)
    else:
      lexer.lexer.truth_value = False

  if verbosity >2: 
    print ('\tEnding the evaluation... of a pattern step')
    print ('\t_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _')

  return lexer.lexer.truth_value, data_cursor_extension, len(pattern_step[group_id-1]) 




# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def parse_semantic (compiledPattern, data, **kwargs): 
  '''
  Parse a compiled pattern and depending on the re method return the recognized pattern over the data 
  '''
  verbosity = 0
  if 'verbosity' in kwargs.keys():
    verbosity = kwargs['verbosity']

  if verbosity >1:
    print ('\t________________________________________________')      
    print ('\tStarting semantic parsing...')  

  l = compiledPattern.getLexer()
  pattern_data_start = 0
  data_cursor = 0
  pattern_cursor = 0
  pattern_steps = l.lexer.pattern_steps
  group_pattern_offsets_group_list = l.lexer.group_pattern_offsets_group_list

  match_on_going = False    # a pattern is being recognized

  group_start_index = []    # the start positions of each recognized group 
  group_end_index = []      # the end positions of each recognized group 

  matcheslist = MatchesList()         # list of matched data

  pattern_cursor_to_data_cursor = {} 

  # # while there is sufficient data to recognize a pattern (! warning some pattern token are ? )
    # len (p.lexer.pattern_steps) minus # ?|*
  while data_cursor < len(data):
    quantifier, step = pattern_steps[pattern_cursor]
    # data_token = data[data_cursor]
    if verbosity >1:
      # print ('\t------------------------------------------------')
      print ('\t_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _')
      print ('\tState: pattern_cursor="{}" quantifier="{}" pattern_step=[{}] data_cursor="{}" data_token="{}" '
        .format(pattern_cursor, quantifier, step, data_cursor, data[data_cursor]))        
      print ('\t_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _')

    # step without quantifier
    if quantifier == None:
      if verbosity >1: print ('\tEvaluating none_quantifier pattern_step')
      step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor, **kwargs)
      if step_evaluation:
        if verbosity >1: print ('\tEvaluation result: match pattern_step')        
        # first pattern step matched
        if not(match_on_going):
          if verbosity >1: print ('\tAction: start recognition and store the data_cursor as a start position')
          group_start_index.append(data_cursor)
          match_on_going = True
        pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor  
        pattern_cursor += 1
      else:
        # abort recognition
        if verbosity >1: print ('\tEvaluation result: unmatch pattern_step')
        if match_on_going:
          if verbosity >1: print ('\tAction: abort recognition')
          group_start_index.pop()
        match_on_going = False
        pattern_data_start = pattern_data_start+1
        pattern_cursor = 0
        pattern_cursor_to_data_cursor = {}
        if l.lexer.pattern_must_match_data_start:
          break

      data_cursor += data_cursor_extension  

    # optional step
    elif quantifier == '?':
      pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor   
      if verbosity >1: print ('\tEvaluating optional pattern_step')
      step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor, **kwargs)
      if step_evaluation:
        if verbosity >1: print ('\tEvaluation result: match optional pattern_step')
        # first pattern step matched
        if not(match_on_going):
          if verbosity >1: print ('\tAction: start recognition and store the data_cursor as a start position')
          match_on_going = True
          group_start_index.append(data_cursor)  
        #pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor   
        data_cursor += data_cursor_extension  
      else:
        if verbosity >1: print ('\tEvaluation result: unmatch optional pattern_step')
      pattern_cursor += 1 

    elif quantifier == '*':
      any_iter  = 0
      pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor   
      if verbosity >1: print ('\tEvaluating any pattern_step')
      step_evaluation = step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor, **kwargs)
      while step_evaluation:
        if verbosity >1: print ('\tEvaluation result: in any pattern_step "{}" iteration, match_on_going="{}", data_cursor="{}", data_token="{}"'
          .format(any_iter, match_on_going, data_cursor, data[data_cursor]))
        if any_iter == 0:
          # first pattern step matched
          if not(match_on_going):
            if verbosity >1: print ('\tAction: start recognition and store the data_cursor as a start position')
            match_on_going = True
            group_start_index.append(data_cursor)   
          #pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor
        data_cursor += data_cursor_extension 
        any_iter += 1
        # case where a complex pattern has one first part being recognized while the data ends
        if data_cursor >= len(data):
          break

        step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor, **kwargs)  

      if verbosity >1: print ('\tEvaluation result: after any pattern_step evaluation : "{}" iteration, match_on_going="{}", data_cursor="{}", data_token="{}"'
          .format(any_iter, match_on_going, data_cursor, data[data_cursor] if data_cursor < len(data) else 'no-more'))

      pattern_cursor += 1 

      if any_iter > 0:
        if verbosity >1: print ('\tEvaluation result: some data_token have been recognized')
        # case where *[ab]b
        if pattern_cursor < len(pattern_steps) :
          next_quantifier, next_step = pattern_steps[pattern_cursor]
          if verbosity >1: print ('\tchecking the *[ab]b case: any_iter="{}", pattern_cursor="{}", next_step="{}", data_cursor="{}", data[data_cursor-1]="{}"'
            .format(any_iter, pattern_cursor, next_step, data_cursor, data[data_cursor - 1]))
          step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor - 1, **kwargs)
          if any_iter > 0 and step_evaluation:
            if verbosity >1: print ('\tAction: modify the cursor to face the case of *[ab]b')
            data_cursor -= data_cursor_extension

    elif quantifier == '+':
      if verbosity >1: print ('\tEvaluating at_least_one pattern_step')
      any_iter  = 0
      step_evaluation = step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor, **kwargs)
      while step_evaluation:
        if verbosity >1: print ('\tEvaluation result: in at_least_one pattern_step "{}" iteration, match_on_going="{}", data_cursor="{}", data_token="{}"'
            .format(any_iter, match_on_going, data_cursor, data[data_cursor]))
        if any_iter == 0:
          # first pattern step matched
          if not(match_on_going):
            if verbosity >1: print ('\tAction: start recognition and store the data_cursor as a start position')
            match_on_going = True
            group_start_index.append(data_cursor)
          pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor      
        data_cursor += data_cursor_extension
        any_iter += 1
        # case where a complex pattern has one first part being recognized while the data ends
        if data_cursor >= len(data):
          break
        step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor, **kwargs)

      if verbosity >1: print ('\tEvaluation result: after at_least_one pattern_step evaluation : "{}" iteration, match_on_going="{}", data_cursor="{}", data_token="{}"'
          .format(any_iter, match_on_going, data_cursor, data[data_cursor] if data_cursor < len(data) else 'no-more'))

      if any_iter > 0: 
        pattern_cursor += 1 
        if verbosity >1: print ('\tEvaluation result:some data_token have been recognized')
        # case where +[b]b to recognize bbb
        if any_iter > 1 and pattern_cursor < len(pattern_steps) : 
        # at least 2 iterations are required, since it is '+', we cannot modify the first one
          next_quantifier, next_step = pattern_steps[pattern_cursor]
          step_evaluation, data_cursor_extension, pattern_cursor_extension = evaluate (l, pattern_steps, pattern_cursor, data, data_cursor - 1, **kwargs)
          if any_iter > 0 and step_evaluation:
            if verbosity >1: print ('\tmodify the cursors to face the case of *[ab]b')
            data_cursor -= data_cursor_extension
      else:
        # abort recognition
        if verbosity >1: print ('\tEvaluation result: no data_token has been recognized')
        if match_on_going:
          if verbosity >1: print ('\tAction: abort recognition')
          group_start_index.pop()
        match_on_going = False
        pattern_data_start = pattern_data_start+1
        pattern_cursor = 0
        data_cursor += 1
        pattern_cursor_to_data_cursor = {}
        if l.lexer.pattern_must_match_data_start:
          break
  

#   # a pattern has been recognized
    #if verbosity >2: 
    #  print ('\t\tpattern_cursor="{}" quantifier="{}" pattern_step=[{}] len(pattern_steps)="{}" data_cursor="{}" data_token="{}" match_on_going="{}"'.format(pattern_cursor, quantifier, step, len(pattern_steps), data_cursor, data_token, match_on_going))        
    if pattern_cursor >= len(pattern_steps):
      if match_on_going:
        group_end_index.append(data_cursor)           
        start = group_start_index[len(group_start_index)-1]
        end = group_end_index[len(group_start_index)-1]
        pattern_cursor_to_data_cursor[pattern_cursor] = data_cursor 
        current_groups = []
        #if verbosity >2: 
        #  print ('\tgroup_pattern_offsets_group_list=', group_pattern_offsets_group_list)
        #  print ('\tpattern_cursor_to_data_cursor=', pattern_cursor_to_data_cursor)
        for s, e in group_pattern_offsets_group_list:
          #current_groups.append([data[start:end], s, e])
          current_groups.append([data[pattern_cursor_to_data_cursor[s]:pattern_cursor_to_data_cursor[e]], pattern_cursor_to_data_cursor[s], pattern_cursor_to_data_cursor[e]])
          #print ('Debug: pattern_cursor_to_data_cursor[{}]={} pattern_cursor_to_data_cursor[{}]={}'.format(s, pattern_cursor_to_data_cursor[s], e, pattern_cursor_to_data_cursor[e]))  

        if verbosity >1: 
          print ('\tSemantic parsing result:') 
          print ('\t\trecognition of a whole pattern') 
          print ('\t\tstore the data_cursor as a end position')
          #print ('\tcreate the Match(start={}, end={}, value={})'.format(start, end, data[start:end]))
          print ('\t\tcreate the Match(groups={})'.format(current_groups))
        #print ('Debug: l.lexer.group_pattern_offsets_group_list=', l.lexer.group_pattern_offsets_group_list)

        #match = Match (start=start, end=end, value=data[start:end])
        #print('Debug: match=', match)
        #matcheslist.append(match)
        #print ('Debug: current_groups=', current_groups)


        if not(l.lexer.pattern_must_match_data_end) or (l.lexer.pattern_must_match_data_end and data_cursor == len(data)): 
          matcheslist.append(Match(groups=current_groups))
        
        # stop parsing after the first match or if findall but only possible match since the pattern_must_match_data_start !
        if l.lexer.re in ['search', 'match'] or l.lexer.pattern_must_match_data_start:  
          break
      else:
        # we are in the case of a pattern made of a single optional step which was not recognized
        # we have to step forward otherwise we fall in an infinite loop
        if verbosity >1: print ('\tcase of a pattern made of a single optional step which was not recognized, we move forward data_cursor')
        data_cursor += 1
         
      pattern_data_start = data_cursor
      pattern_cursor = 0
      match_on_going = False
      if l.lexer.pattern_must_match_data_start:
        break
    else: 
      if verbosity >1: print ('\tSemantic parsing result:\n\t\tsome pattern recognition may be on going but none full form has been recognized after processing this pattern_step')
  
  if verbosity >1:       
    #print('Debug: matcheslist=', matcheslist)
    print ('\tEnding semantic parsing.')  
  return matcheslist


# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#  MAIN
# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

if __name__ == '__main__':  
  start = 0
  end = 1
  data =  [{'raw': 'It', 'pos': 'PRP'}, {'raw': 'is', 'pos': 'VBZ'}, {'raw': 'fast', 'pos': 'JJ'}, {'raw': 'easy', 'pos': 'JJ'}, {'raw': 'and', 'pos': 'CC'}, {'raw': 'funny', 'pos': 'JJ'}, {'raw': 'to', 'pos': 'TO'}, {'raw': 'write', 'pos': 'VB'}, {'raw': 'regular', 'pos': 'JJ'}, {'raw': 'expressions', 'pos': 'NNS'}, {'raw': 'with', 'pos': 'IN'}, {'raw': 'Pyrata', 'pos': 'NNP'}]

  print ('Debug: create the Match(start={}, end={}, value={})'.format(start, end, data[start:end]))
  match = Match (start=start, end=end, value=data[start:end])
  print('Debug: match=', match)