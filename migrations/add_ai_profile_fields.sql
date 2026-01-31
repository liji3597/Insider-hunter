-- 数据库迁移脚本：添加 AI 交易者画像分析字段
-- 用途：为 trader_profiles 表添加 AI 分析相关的新字段
-- 运行方式：psql -h localhost -U hunter -d polymarket_db -f migrations/add_ai_profile_fields.sql

-- 添加 AI 分析字段
ALTER TABLE trader_profiles
ADD COLUMN IF NOT EXISTS trading_style VARCHAR(50),
ADD COLUMN IF NOT EXISTS risk_preference VARCHAR(20),
ADD COLUMN IF NOT EXISTS ai_analysis TEXT;

-- 添加注释
COMMENT ON COLUMN trader_profiles.trading_style IS '交易风格：激进/稳健/保守/投机/对冲';
COMMENT ON COLUMN trader_profiles.risk_preference IS '风险偏好：高/中/低';
COMMENT ON COLUMN trader_profiles.ai_analysis IS 'AI 深度分析文本';

-- 更新 label 字段注释
COMMENT ON COLUMN trader_profiles.label IS 'AI 生成的标签（如：激进型政治预测专家）';

-- 显示结果
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'trader_profiles'
ORDER BY ordinal_position;
