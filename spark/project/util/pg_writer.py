#util/pg_writer.py

from util.table_conflict import CONFLICT_CLAUSES, DEFAULT_CONFLICT_CLAUSE

def get_postgres_writer(pg_conf, log):
    """
    Returns a function that writes a dictionary of table_name: DataFrame
    to corresponding Postgres tables.
    """
    def write_to_postgres_multi(batch_dfs: dict, batch_id: int):
        """
        batch_dfs: dict with keys as table names and values as DataFrames
        batch_id:  current microbatch ID (int)
        """

        for table_name, df in batch_dfs.items():
            if df is None or df.rdd.isEmpty():
                log.info(f"[{table_name}] Batch {batch_id} is empty. Skipping.")
                continue

            # Lookup the ON CONFLICT clause for this table, or use the default:
            conflict_clause = CONFLICT_CLAUSES.get(table_name, DEFAULT_CONFLICT_CLAUSE)

            try:
                df\
                .write\
                .format('jdbc')\
                .option('dbtable', table_name)\
                .options(**pg_conf)\
                .mode('append')\
                .option('upsert', 'true')\
                .option('postUpsertSQL', conflict_clause)\
                .save()

                log.info(f"Batch {batch_id}: {df.count()} rows written to {table_name}")
            
            except Exception as e:
                log.error(f"Error writing batch {batch_id} to table {table_name}: {e}")
    return write_to_postgres_multi