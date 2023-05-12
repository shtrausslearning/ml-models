
from mllibs.nlpm import nlpm
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

palette = ['#b4d2b1', '#568f8b', '#1d4a60', '#cd7e59', '#ddb247', '#d15252']
palette_rgb = [hex_to_rgb(x) for x in palette]

# interaction & tect interpreter class
 
class nlpi(nlpm):
    
    # instantiation requires module
    
    def __init__(self,module=None,verbose=0):
        
        self.module = module                  # collection of modules
        self.data = {}                        # dictionary for storing data
        self.dsources = {}                    # store all data source keys
        self.token_data = []                  # store all token data
        self.verbose = verbose                # print output text flag

        nlpi.memory_output = []          # keep order of stored operations
        nlpi.memory_name = []                      # store order of executed tasks
        nlpi.memory_stack = []                # memory stack of task information
        nlpi.iter = -1                         # execution iteraction counter
        
        # class plot parameters
        nlpi.pp = {'alpha':1,'mew':0,'mec':'k','fill':False,'stheme':palette_rgb,'s':30}
        
    def setpp(self,params:dict):
        if(type(params) is not dict):
            print("plot parameter dictionary: {'alpha':1,'mew':1,'mec':'k',...}")
        else:
            nlpi.pp.update(params)
            print('plot parameter updated!')
   
    @classmethod
    def resetpp(cls):
        nlpi.pp = {'alpha':1,'mew':0,'mec':'k','fill':False,'stheme':palette_rgb,'s':30}

    # Check all available data sources, update dsources dictionary
                    
    def check_dsources(self):
        
        lst_data = list(self.data.keys())            # data has been loaded
        self.dsources = {'inputs':lst_data}
                
        print('inputs:')
        print(lst_data,'\n')
        
               
        
    def store(self,data,name):
        self.data[name] = data
        
    def debug(self):
        
        print('module sumamry:')
        self.module.mod_summary
        print('')
        
        print('token information')
        print(self.token_info)
        print('')
        
        print('interpreter module arguments')
        print(self.module_args)
        print('')

    @staticmethod
    def exists(var):
         return var in globals()
        
    ''' Check if token names are in data sources '''
    
    # get token data
    def get_td(self,token):
        return self.token_data[int(self.token_info.loc[token,'data'])]
    
    # get last result
    
    def glr(self):
        return nlpi.memory_output[nlpi.iter]
    
    def check_data(self):
        
        # intialise data column in token info
        self.token_info['data'] = np.nan  # store data type if present
        self.token_info['dtype'] = np.nan  # store data type if present
        self.token_info['data'] = self.token_info['data'].astype('Int64')
                
        ''' keys '''
        # list all available data sources
        lst_data = list(self.data.keys())            # lsit of data has been loaded
        lst_globals = list(globals().keys())         # list of global variable names
        lst_all = [lst_data,lst_globals] # list of all data source names
        
        ''' values '''
        # available data locations
        sources = [self.data,globals()]
        
        # cycle through all available key names    
        dict_tokens = {}
        for ii,lst in enumerate(lst_all):        
            for source_name in lst:
                if(source_name in self.tokens):     
                    if(source_name in dict_tokens):
                        print('another data source found, overwriting')
                        dict_tokens[source_name] = sources[ii][source_name]
                    else:
                        dict_tokens[source_name] = sources[ii][source_name]
                    
        ''' if we have found matching tokens '''
                    
        if(len(dict_tokens) is not 0):
            for token,value in dict_tokens.items():
                
                # store data (store index of stored data)
                self.token_info.loc[token,'data'] = len(self.token_data) 
                self.token_data.append(value)   
                
                # store data type
                if(type(value) is eval('pd.DataFrame')):
                    self.token_info.loc[token,'dtype'] = 'pd.DataFrame'
                elif(type(value) is eval('pd.Series')):
                    self.token_info.loc[token,'dtype'] = 'pd.Series'
                elif(type(value) is eval('dict')):
                    self.token_info.loc[token,'dtype'] = 'dict'
                elif(type(value) is eval('list')):
                    self.token_info.loc[token,'dtype'] = 'list'   
                elif(type(value) is eval('str')):
                    self.token_info.loc[token,'dtype'] = 'str'   
        else:
            pass
        
        # check if tokens belong to dataframe column
        self.token_info['column'] = np.nan
        self.token_info['key'] = np.nan
        self.token_info['index'] = np.nan

        ''' Check Inside '''
        # check if tokens match dataframe column,index & dictionary keys
        temp = self.token_info
        
        # possible multiple dataframe
        ldfs = temp[temp['dtype'] == 'pd.DataFrame']

        # i - token name; j token dataframe
        for i,j in ldfs.iterrows():

            # df column & index names
            df_columns = list(self.get_td(i).columns)
            df_index = list(self.get_td(i).index)

            tokens = list(temp.index)
            for token in tokens:
                if(token in df_columns):
                    temp.loc[token,'column'] = j.name 
                if(token in df_index):
                    temp.loc[token,'column'] = j.name

        ldfs = temp[temp['dtype'] == 'dict']

        for i,j in ldfs.iterrows():

            # dictionary keys
            dict_keys = list(self.get_td(i).keys())
            tokens = list(temp.index)

            for token in tokens:
                if(token in dict_keys):
                    temp.loc[token,'key'] = j.name 
                    
    
    @staticmethod
    def n_grams(tokens,n):
        lst_bigrams = [' '.join(i) for i in [tokens[i:i+n] for i in range(len(tokens)-n+1)]]
        return lst_bigrams
    
    def __getitem__(self,command:str):
        self.exec(command,args=None)
        
    def exec(self,command:str,args:dict=None):                        
        self.do(command=command,args=args)
  
    '''
    
    Execute everything relevant for single command 
    
    '''
    
    def do_predict(self):
    
        ''' module model prediction '''
        ms_name = self.module.test_name('ms',self.command)
        
#         recommender_module = self.module.recommend_module(self.command) # module recommend
#         print(ms_name,recommender_module)
        
        
        if(self.verbose): print(f'using module: {ms_name}')
        
        # Available tasks 
    
        lst_tasks = self.module.module_task_name[ms_name]
        t_pred_p = self.module.test(ms_name,self.command)  
        t_pred = np.argmax(t_pred_p)
    
        # [2] name o the module task to be called
        t_name = lst_tasks[t_pred] 
        
        if(self.verbose): print(f'Executing Module Task: {t_name}')

        # store predictions
        self.task_pred = t_pred
        self.task_name = t_name
        self.module_name = ms_name
    
    @staticmethod
    def convert_to_df(ldata):
        
        if(type(ldata) is list or type(ldata) is tuple):
            return pd.Series(ldata).to_frame()
        elif(type(ldata) is pd.Series):
            return ldata.to_frame()
        else:
            raise TypeError('Could not convert input data to dataframe')
            
    @staticmethod
    def convert_to_list(ldata):
        
        if(type(data) is str):
            return [ldata]
        else:
            raise TypeError('Could not convert input data to list')
    
    def sort_module_args(self):
        
        # acceptable data types
        accept_types = (str,list,dict,pd.DataFrame,pd.Series)
        
        in_format = self.module.mod_summary.loc[self.task_name,'input_format']
        if(self.verbose): print(f'required input format for task {self.task_name}: {in_format}')
        
        # dataframe containing information of data sources of tokens
        available_data = self.token_info[['data','dtype']].dropna() 
        len_data = len(available_data)
        
        # if we only have one type, then it is the data we need
        if(len_data == 1):            
            
            # if available data matches input function input requirement
            ldtype = available_data.loc[available_data.index,'dtype'].values[0]
            ldata = self.get_td(available_data.index)
            
            if(ldtype == in_format):
                if(self.verbose): print('found matching type data!')
                self.module_args['data'] = self.get_td(available_data.index)
            else:
                if(self.verbose): print('trying to convert data to required format!')
                # try to convert input data to dataframe
                if(in_format == 'pd.DataFrame'):
                    self.module_args['data'] = self.convert_to_df(ldata)
                elif(in_format == 'list'):
                    self.module_args['data'] = self.convert_to_list(ldata)
            
        elif(len_data > 1):
            data_type_match = available_data[available_data['dtype'] == in_format]
            if(len(data_type_match) == 1):
                self.module_args['data'] = self.get_td(data_type_match.index)
        else:
            raise NameError('Function input data has not been set!')
                        
#       read output format          
        out_format = self.module.mod_summary.loc[self.task_name,:]['output_format']    
        
        ''' 
        
        Check for column related tokens 
        
        '''
        
        # we actually have column (from dataframe) data
    
        col_data = self.token_info['column'].dropna()
        len_col_data = len(col_data)
        column_tokens = list(col_data.index)
        
        if(len_col_data is not 0):            
            for token in column_tokens:
                
                if(out_format == 'figure'):   
                    if(self.tokens[self.tokens.index(token)-1] == 'x'):
                        self.module_args['x'] = token
                    if(self.tokens[self.tokens.index(token)-1] == 'y'):
                        self.module_args['y'] = token
                    if(self.tokens[self.tokens.index(token)-1] == 'hue'):
                        self.module_args['hue'] = token
                    if(self.tokens[self.tokens.index(token)-1] == 'col'):
                        self.module_args['col'] = token
                    if(self.tokens[self.tokens.index(token)-1] == 'row'):
                        self.module_args['row'] = token
                    if(self.tokens[self.tokens.index(token)-1] == 'target'):
                        self.module_args['target'] = token
                
                        
        '''
        
        Check general plot setting tokens
        
        '''
        
        for ii,token in enumerate(self.tokens):
            if(self.tokens[self.tokens.index(token)-1] == 'col_wrap'):
                self.module_args['col_wrap'] = token
            if(self.tokens[self.tokens.index(token)-1] == 'kind'):
                self.module_args['kind'] = token                                       
                    
        ''' add found column tokens to subset '''
        
        # for dataframe case, columns are our subset
        if(in_format == 'pd.DataFrame'):
            self.module_args['subset'] = column_tokens
        
        
        ''' find feature matrix '''
        
        # Attempt to find feature matrix & target variable data
        # Data needs to be defined separately (atm)
        
        lst_feats = ['matrix','features','fm']
        lst_target = ['target','labels']
        
        for ii,token in enumerate(self.tokens):
            
            if(token in lst_feats):
                self.module_args['features'] = self.get_td(self.tokens[ii+1])
                
            #if(token in lst_target):
             #   self.module_args['target'] = self.get_td(self.tokens[ii+1])
                
    # tokenisers, return list of tokens          
                
    @staticmethod
    def nltk_tokeniser(text):
        return word_tokenize(text)
           
    def do(self,command:str,args:dict):
        
        '''
        
        Module argument
        
        '''
       
        # user input command
        self.command = command
        
        # Initialise arguments dictionary
       
        self.module_args = {'pred_task': None, 'data': None,'subset': None,
                            'features': None, 'target' : None,
                            'x': None, 'y': None, 'hue': None,'col':None,'row':None,
                            'col_wrap':None,'kind':'scatter',
                            'figsize':[None,None]}
        
        # update argument dictionary if it was set
        
        if(args is not None):
            self.module_args.update(args)
            
        ''' Tokenise Input Command '''
        
        # tokenise input, unigram. bigram and trigram
        self.tokens = self.nltk_tokeniser(self.command)    
        self.bigram_tokens = self.n_grams(self.tokens,2)
        self.trigram_tokens = self.n_grams(self.tokens,3)
        
        uni = pd.Series(self.tokens).to_frame()
        bi = pd.Series(self.bigram_tokens).to_frame()
        tri = pd.Series(self.trigram_tokens).to_frame()
       
        uni['type'] = 'uni'
        bi['type'] = 'bi'
        tri['type'] = 'tri'
        
        self.token_info = pd.concat([uni,bi,tri],axis=0)      
        self.token_info.columns = ['token','type']
        self.token_info.index = self.token_info['token']
        del self.token_info['token']
        
        ''' Determine which models to load & predict which task to execute '''
        
        self.do_predict() # task_pred, module_name
        
        ''' Some logical tests '''
        
        self.check_data()
        self.sort_module_args()
             
        '''
            
        Iteration Process
        
        '''
        
        # activate relevant class & pass arguments
        nlpi.iter += 1
        
        self.module_args['pred_task'] = self.task_name
        nlpi.memory_name.append(self.task_name)  # list of executed tasks
        task_info = self.module.mod_summary.loc[nlpi.memory_name[nlpi.iter]] # task information series
        nlpi.memory_stack.append(task_info)
        nlpi.memory_info = pd.concat(self.memory_stack,axis=1) # stack task information order
        
        # activate function
        self.module.functions[self.module_name].sel(self.module_args)
        
        # if not data has been added
        if(len(nlpi.memory_output) == nlpi.iter+1):
            pass
        else:
            nlpi.memory_output.append(np.nan) # initialise output data (overwritten in module.function
        