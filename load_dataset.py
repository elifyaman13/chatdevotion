from datasets import load_dataset
import pandas as pd
import json
import os


dataset = load_dataset("EmoCareAI/Psych8k", split="train")


print(dataset[0:3])


inputs = dataset["input"]
outputs = dataset["output"]


df_psych8k = pd.DataFrame({
    "user_input": inputs,
    "gpt_response": outputs
})

# CSV olarak kaydet
df_psych8k.to_csv("psych8k_cleaned.csv", index=False, encoding="utf-8-sig")
print("✅ psych8k_cleaned.csv dosyası kaydedildi.")


manuel_dosya_yolu = "guncellenmis_psikolojik_veri_seti_chatbot.xlsx"
if os.path.exists(manuel_dosya_yolu):
    df_manual = pd.read_excel(manuel_dosya_yolu)
    df_manual_subset = df_manual[["İçerik", "Psikolojik Yorum"]].rename(
        columns={"İçerik": "user_input", "Psikolojik Yorum": "gpt_response"}
    )
    df_combined = pd.concat([df_psych8k, df_manual_subset], ignore_index=True).dropna()

    
    with open("data/gpt_context_data.json", "w", encoding="utf-8") as f:
        json.dump(df_combined.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
    print("✅ gpt_context_data.json dosyası oluşturuldu.")
else:
    print("ℹ️ Manuel veri dosyası bulunamadı, sadece Psych8k işlendi.")




