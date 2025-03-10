create database if not exists default on cluster cluster_2S_2R;

CREATE TABLE IF NOT EXISTS real_estate_local ON CLUSTER cluster_2S_2R
(
    Title           String,
    PropertySize    UInt32,
    TotalPrice      Float64,
    PricePerMeter   Float64,
    RoomCount       UInt8,
    BuildYear       UInt16,
    FloorNumber Nullable(UInt8),
    TotalFloors Nullable(UInt8),
    Characteristics String,
    Features        String,
    Description     String,
    URL             String,
    CrawlDate       DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/real_estate', '{replica}')
ORDER BY CrawlDate;


CREATE TABLE IF NOT EXISTS gold_data_local ON CLUSTER cluster_2S_2R
(
    id      UInt64,
    title   String,
    price   Float64,
    date    Date,
    datetime DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/gold_data', '{replica}')
ORDER BY id;


CREATE TABLE IF NOT EXISTS dollar_data_local ON CLUSTER cluster_2S_2R
(
    id      UInt64,
    title   String,
    price   Float64,
    date    Date,
    datetime DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dollar_data', '{replica}')
ORDER BY id;


-- Step 2: Create Distributed Tables (To Query Across All Nodes)
CREATE TABLE IF NOT EXISTS real_estate ON CLUSTER cluster_2S_2R AS real_estate_local
ENGINE = Distributed(cluster_2S_2R, default, real_estate_local, rand());

CREATE TABLE IF NOT EXISTS gold_data ON CLUSTER cluster_2S_2R AS gold_data_local
ENGINE = Distributed(cluster_2S_2R, default, gold_data_local, rand());

CREATE TABLE IF NOT EXISTS dollar_data ON CLUSTER cluster_2S_2R AS dollar_data_local
ENGINE = Distributed(cluster_2S_2R, default, dollar_data_local, rand());