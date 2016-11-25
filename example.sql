/*
-- rpt_test_example --
-- Created on 2016-11-23 by levi.kanwischer --
-- Updated on 2016-11-23 by levi.kanwischer --
*/

-- Set database of target table
use test;

-- Create target table if it doesn't already exist
create table test_jinja2 if not exists (
    id int
    , test varchar(10)
    , insert_time timestamp
    )
partition on id
store as parquet
;

-- Grant external access to target table
grant select on test_jinja2 to group TESTGROUP;

-- Drop processing dates from target table
{% for date in dates %}
alter table test_jinja2 drop partition date = "{{date}}";
{% endfor %}

-- Insert processed raw data into target table
insert into test_raw as (
    select
        id
        , test
        , current_time as insert_time
    from
        test
    where
        day between "{{start_date}}" and "{{end_date}}"
    )
;