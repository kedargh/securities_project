CREATE OR REPLACE FUNCTION pg_execute(query text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE query;
END;
$$;


