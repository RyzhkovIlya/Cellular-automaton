class Corr_automatat():
    import pandas as pd
    import numpy as np
    def __init__(self, data:pd.DataFrame, 
                name_item = None, 
                name_user = None,
                number_items:int = None,
                number_users:int = None,
                num_layers:int = 1, 
                threshold:float = 0.5, 
                method:str = "moore"):
        """
        Args:
            data (pd.DataFrame): Dataframe User-Item containing 0 and 1.
            name_item (optional): Item name(name film, goods, product, etc.). Defaults to None.
            name_user (optional): User name(First name, Second name, number name, etc.). Defaults to None.
            num_layers (int, optional): Number of counting environment layers. Defaults to 1.
            threshold (float, optional): Threshold for final score. Defaults to 0.5.
            method (str, optional): Method counting environment ["moore", "neumann"]. Defaults to "moore".
            number_items (int, optional): Count return items. Only for "number_item"==None. Defaults to 5.
            number_users (int, optional): Count return users. Only for "number item"==None. Defaults to 5.
        """
        self.data = data
        self.name_item = name_item
        self.name_user = name_user
        self.num_layers = num_layers
        self.threshold = threshold
        self.method = method
        self.number_items = number_items
        self.number_users = number_users
        
    def create_user_corr(self, name_user)->pd.DataFrame:
        """
        Function create new dataframe by user correlation

        Args:
            name_user: User name(First name, Second name, number name, etc.)
        
        Returns:
            pd.DataFrame: Return new dataframe by user correlation
        """
        user_like = self.data.T.corrwith(self.data.loc[name_user])
        corr_user = pd.DataFrame(user_like, columns=['Correlation'])
        corr_user.dropna(inplace=True)
        corr_user.sort_values(by="Correlation",ascending=False, inplace=True)

        all_df = self.data.join(corr_user)
        all_df.sort_values("Correlation", ascending=False, inplace=True)
        return all_df

    def create_item_corr(self, data:pd.DataFrame, name_item:str)->list:
        """
        Function create new dataframe by user correlation and return indexes

        Args:
            data (pd.DataFrame): Dataframe with user correlation
            name_item: Item name(name film, goods, product, etc.)

        Returns:
            list: List with item indexex
        """
        movies_like_item = data.corrwith(data[name_item])
        corr_item = pd.DataFrame(movies_like_item, columns=['Correlation'])
        corr_item.dropna(inplace=True)
        corr_item.sort_values('Correlation', ascending=False, inplace=True)
        forrest_index = corr_item.index.tolist()
        return forrest_index

    def move_col_row(self, data:pd.DataFrame, name_item, name_user)->[pd.DataFrame, pd.DataFrame]:
        """
        Function transform dataframe for counting score

        Args:
            data (pd.DataFrame): Dataframe with user correlation and item correlation
            name_item: Item name(name film, goods, product, etc.)
            name_user: User name(First name, Second name, number name, etc.)

        Returns:
            [pd.DataFrame, pd.DataFrame]: Two dataframe [Intermediate dataframe, major datarame]
        """
        data.insert(self.num_layers+1, name_item, value=data.iloc[:, 0].values, allow_duplicates=True)
        data_new = data.iloc[:, 1:]
        data = data.T.drop_duplicates().T
        data_transp = data_new.T
        data_transp.insert(self.num_layers+1, name_user, value=data_transp.iloc[:, 0].values, allow_duplicates=True)
        data_transp = data_transp.iloc[:, 1:]
        data_1 = data_transp.T
        return data_1, data
    
    def count_score(self, sample_data:pd.DataFrame)->float:
        """
        Function counts score
        
        Args:
            sample_data (pd.DataFrame): Dataframe for counts score

        Returns:
            float: Estimate score
        """
        main_score = 0
        if self.method == "moore":
            sum_one = sum(sample_data.sum())
            all_elem = (self.num_layers*2+1)**2 -1
            main_score = sum_one/all_elem
            return main_score

        elif self.method == "neumann":
            one_count = 0
            zero_count = -2
            one_col = sample_data.iloc[:, self.num_layers].values.tolist().count(1)
            zero_col = sample_data.iloc[:, self.num_layers].values.tolist().count(0)
            one_row = sample_data.iloc[self.num_layers].values.tolist().count(1)
            zero_row = sample_data.iloc[self.num_layers].values.tolist().count(0)
            one_count += one_col+one_row
            zero_count += zero_col+zero_row
            main_score = one_count/(one_count+zero_count)
            return main_score

    def cellular_automatat(self)->pd.DataFrame:
        """
        Major function

        Returns:
            pd.DataFrame: Return Major Dataframe
        """
        methods = ["moore", "neumann"]
        
        condition = [self.num_layers > min(self.data.shape[0]//2, self.data.shape[1]//2) or self.num_layers <= 0, 
                    self.name_item != None and self.name_user != None and self.data.loc[self.name_user, self.name_item] != 0.0, 
                    self.method not in methods,
                    self.number_items != None and self.number_items > self.data.shape[1], 
                    self.number_users != None and self.number_users > self.data.shape[0],
                    self.threshold >= 1.0 or self.threshold <= 0.0,
                    self.number_items != None and self.number_items <= 0,
                    self.number_users != None and self.number_users <= 0]
        label = ["Too many layers of counting or num_layers <= 0", 
                f"Your item {self.name_item} is already rated by user {self.name_user}", 
                f"Not found method {self.method}, try one of the available - {methods}", 
                "Parameter 'number_items' is so large",
                "Parameter 'number_users' is so large", 
                "Parameter 'threshold' is error. Must be (0, 1)",
                "Parametrt number_items must be [1, data.shape[1]",
                "Parametrt number_users must be [1, data.shape[0]"]
        output = np.select(condition, label)
        if output != "0":
            print(output)
            return
        
        if self.name_item != None and self.name_user != None:
            all_data = self.create_user_corr(name_user = self.name_user)
            indexes = self.create_item_corr(data = all_data, 
                                            name_item = self.name_item)
            new_data, data = self.move_col_row(data = all_data[indexes], 
                                            name_item = self.name_item, 
                                            name_user = self.name_user)        
            sample_data = new_data.iloc[:self.num_layers*2+1, :self.num_layers*2+1]
            
            main_score = self.count_score(sample_data = sample_data)
            if main_score > self.threshold:
                print(f"Item {self.name_item} approach for User {self.name_user}")
                return data, self.name_item
            else: 
                print(f"Item {self.name_item} doesn't approach for User {self.name_user}")
                return data, self.name_item
            
        if self.name_item == None and self.name_user != None:
            if self.number_items == None:
                print('Expected input parameter "number_items" or "name_item"')
                return
            scores = {}
            for item in self.data.loc[self.name_user, :][self.data.loc[self.name_user, :]==0].index:
                all_data = self.create_user_corr(name_user = self.name_user)
                indexes = self.create_item_corr(data = all_data, 
                                                name_item = item)
                new_data, data = self.move_col_row(data = all_data[indexes], 
                                                name_item = item, 
                                                name_user = self.name_user)        
                sample_data = new_data.iloc[:self.num_layers*2+1, :self.num_layers*2+1]
                main_score = self.count_score(sample_data = sample_data)
                if main_score > self.threshold:
                    scores[item] = main_score
            print(f"For User {self.name_user} approach follow {self.number_items} items: {sorted(scores, key=scores.get, )[::-1][:self.number_items]}")
            return data, sorted(scores, key=scores.get, )[::-1][:self.number_items]
        
        if self.name_item != None and self.name_user == None:
            if self.name_user == None:
                print('Expected input parameter "number_users" or "name_user"')
                return
            scores = {}
            for user in self.data.loc[:, self.name_item][self.data.loc[:, self.name_item]==0].index:
                all_data = self.create_user_corr(name_user = user)
                indexes = self.create_item_corr(data = all_data, 
                                                name_item = self.name_item)
                new_data, data = self.move_col_row(data = all_data[indexes], 
                                                name_item = self.name_item, 
                                                name_user = user)        
                sample_data = new_data.iloc[:self.num_layers*2+1, :self.num_layers*2+1]
                main_score = self.count_score(sample_data = sample_data)
                if main_score > self.threshold:
                    scores[user] = main_score
            print(f"For Item {self.name_item} approach follow {self.number_users} users: {sorted(scores, key=scores.get)[::-1][:self.number_users]}")
            return data, sorted(scores, key=scores.get, )[::-1][:self.number_users]