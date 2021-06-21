class AggLumDataTable():
    #creates a LumData object for each path in list
    #aggregates the LumData.table_name for each of those LumData objects
    #adding new features taken from the file name so that rows
    #can now be filtered using m_lab_id, PBMC_type, and time_point
    #this would allow more complex graphing of summary plots from a single table
    def __init__(self, file_list: List[str], plate_map: str, table_name: str='Result'):
        self.name_parts = self._name_parts(file_list)
        self.table = self._aggregate_table(file_list, plate_map, table_name)

    def _name_parts(self, paths):
        """
        date_time	20210513_161711
        m_lab_id	CH-BR-162
        PBMC_type	MR
        file_name	CH-BR-162_MR_T48h_20210513_161711.csv
        basename	/Volumes/modeling/Drug Assays/Roche_Luminex
        no_ext          CH-BR-162_MR_T48h_20210513_161711
        ext	        .csv
        time_point	T48h
        path	        /Volumes/modeling/Drug Assays/Roche_Luminex/CH-BR-162_MR_T48h_20210513_161711.csv
        """
        dict_list = []
        query = re.compile(r'(?P<path>(?P<basename>.*)\/(?P<file_name>(?P<no_ext>(?P<m_lab_id>[A-Z]{2,}-[A-Z]{2,}-[0-9]{2,})_(?P<PBMC_type>HR|MR|LR)_(?P<time_point>.*?)_(?P<date_time>[0-9]{4,4}[0-9]{2,2}[0-9]{2,2}_[0-9]{6,6}))(?P<ext>\.\w*)))')
        for p in paths:
            m = re.match(query, p)
            assert m
            dict_list.append(m.groupdict())
        return dict_list

    def _aggregate_table(self, file_list, plate_map, table_name):
        lds = []
        for f in file_list:
            ld = LumData(f,plate_map)
            assert ld
            lds.append(ld)

        df_list = []
        for i,ld in enumerate(lds):
            name_parts = self.name_parts[i]
            table_copy = getattr(ld, table_name).copy()
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
