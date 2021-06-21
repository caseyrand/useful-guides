class AggLDHTable():
    """
    Aggregate tables hold all data from a set of related experiments from a file_list and plate_map. 
    AggLDHTable parses metadata from the file names provided and creates a dictionary containing the matched 
    file name pieces. Some of this meta-data is added as columns to the AggLDHTable. This provides one
    data table holding the entire set of related experiments, all time points, all plates, all conditions. 
    This allows complex grouping and graphing as rows can now be filtered for any required m_lab_id, PBMC_type,
    time_point, etc.
    All data is accessed through attributes.
    No further data alterations are allowed. So there are no instance methods.
    
    Attributes:
    name_parts      list of dictionaries containing all matched name parts. List[Dict[str,str]]
    table           aggregated table data. (pd.DataFrame)
    """
    def __init__(self, file_list: List[str], plate_map: str):
        self.name_parts = self._name_parts(file_list)
        self.table = self._aggregate_table(file_list, plate_map)

    def _name_parts(self, paths):
        """
        date_time	20210513_161711
        m_lab_id	CH-BR-162
        PBMC_type	MR
        file_name	CH-BR-162_MR_T48h_20210513_161711.csv
        basename	/Volumes/modeling/Drug Assays/Roche_LDHv1
        no_ext          CH-BR-162_MR_T48h_20210513_161711
        ext	        .csv
        time_point	T48h
        path	        /Volumes/modeling/Drug Assays/Roche_LDHv1/CH-BR-162_MR_T48h_20210513_161711.xml
        """
        dict_list = []
        query = re.compile(r'(?P<path>(?P<basename>.*)\/(?P<file_name>(?P<no_ext>(?P<m_lab_id>[A-Z]{2,}-[A-Z]{2,}-[0-9]{2,})_(?P<PBMC_type>HR|MR|LR)_(?P<time_point>.*?)_(?P<date_time>[0-9]{4,4}[0-9]{2,2}[0-9]{2,2}_[0-9]{6,6}))(?P<ext>\.\w*)))')
        for p in paths:
            m = re.match(query, p)
            assert m
            dict_list.append(m.groupdict())
        return dict_list

    def _aggregate_table(self, file_list, plate_map):
        lds = []
        for f in file_list:
            ld = LDH_Data(f,plate_map)
            assert ld
            lds.append(ld.transformed_table)

        df_list = []
        for i,ld in enumerate(lds):
            name_parts = self.name_parts[i]
            #table_copy = getattr(ld, table_name).copy()
            table_copy = ld.copy()
            table_copy.insert(0, 'time_point', name_parts['time_point'] )
            table_copy.insert(0, 'PBMC_type', name_parts['PBMC_type'] )
            table_copy.insert(0, 'm_lab_id', name_parts['m_lab_id'])
            df_list.append(table_copy)

        aggregated = pd.concat(df_list, ignore_index=True)
        return aggregated

    def write(self, path):
        """
        Writes the aggregate table to a specified path.
        If the directory does not exist, it will take care of adding necessary directories.
        """
        path_dir = os.path.dirname(path)
        os.makedirs(path_dir, exist_ok=True)
        self.table.to_csv(path, index=False)
