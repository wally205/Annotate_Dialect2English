import pandas as pd
import os
from dotenv import load_dotenv
from label_studio_sdk.client import LabelStudio

# ============================================================
# Config
# ============================================================
load_dotenv()

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY')

INPUT_FILE = 'train/.csv'
PROJECT_TITLE_NO_MAJORITY = 'Train set Review (No Majority)'

# ============================================================
# Labeling Config - NO MAJORITY TASKS
# ============================================================
LABELING_CONFIG_NO_MAJORITY = '''<View className="custom-font" style="font-family: Arial, sans-serif !important;">
  <Style>
    .custom-font, .custom-font *, .ls-text, .htx-text { 
        font-family: "Arial", sans-serif !important; 
    }
  </Style>
  <Header value="Vietnamese (Standard)" size="2" style="font-family: Arial, sans-serif;" />
  <Text name="standard" value="$standard" granularity="word" />

  <View style="margin:12px 0; padding:12px 16px; border-radius:6px; background:#fff3e0; border-left:4px solid #ff9800;">
    <Text name="task_info" value="$task_info" />
  </View>

  <View style="margin-top:12px; padding:12px; background:#fafafa; border:1px solid #e0e0e0; border-radius:6px;">
    <Header value="Candidate A" size="4" />
    <Text name="candidate_a" value="$candidate_a" />
  </View>

  <View style="margin-top:8px; padding:12px; background:#fafafa; border:1px solid #e0e0e0; border-radius:6px;">
    <Header value="Candidate B" size="4" />
    <Text name="candidate_b" value="$candidate_b" />
  </View>

  <View style="margin-top:8px; padding:12px; background:#fafafa; border:1px solid #e0e0e0; border-radius:6px;">
    <Header value="Candidate C" size="4" />
    <Text name="candidate_c" value="$candidate_c" />
  </View>

  <View style="margin-top:16px;">
    <Header value="Your Decision" size="3" />
    <Choices name="decision" toName="standard" choice="single" required="true">
      <Choice value="Choose A" />
      <Choice value="Choose B" />
      <Choice value="Choose C" />
      <Choice value="Re-translate" />
    </Choices>
  </View>

  <!-- Conditional view when Re-translate is selected -->
  <View visibleWhen="choice-selected" whenTagName="decision" whenChoiceValue="Re-translate" style="margin-top:12px; padding:16px; border:1px solid #bbdefb; background:#e3f2fd; border-radius:6px;">
    <Header value="New Translation" size="4" />
    <TextArea name="new_translation" toName="standard"
              placeholder="Write your translation here..."
              maxSubmissions="1" editable="true" />
  </View>
</View>'''


def build_tasks(df):
    """Tạo danh sách tasks cho Label Studio theo loại."""
    tasks = []

    for idx, row in df.iterrows():
        task_data = {
            'original_id': int(row.get('original_id', idx)),
            # 'split_source': row.get('split_source', ''),
            'standard': row['standard'],
            'candidate_a': row['A'],
            'candidate_b': row['B'],
            'candidate_c': row['C'],
        }

        task_data['winner'] = 'None'
        task_data['task_info'] = (
            'NO MAJORITY — 3 judges chose 3 different candidates. '
            'Please Choose the best (A/B/C) or Re-translate.'
        )

        tasks.append({'data': task_data})

    return tasks


def main():
    if not LABEL_STUDIO_API_KEY:
        print('ERROR: LABEL_STUDIO_API_KEY not found in .env')
        return

    # 1. Read and split data
    df = pd.read_csv(INPUT_FILE)
    
    # Thay thế các giá trị NaN bằng None (null trong JSON) hoặc chuỗi rỗng
    # để tránh lỗi 'NaN' khi gửi payload JSON lên Label Studio
    df = df.fillna('')

    print(f'Loaded {len(df)} samples total.')

    # 2. Connect
    print(f'\nConnecting to {LABEL_STUDIO_URL}...')
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)

    # 3. Create No Majority Project
    if len(df) > 0:
        print(f'\nCreating project: {PROJECT_TITLE_NO_MAJORITY}')
        tasks_no_majority = build_tasks(df)
        
        proj_no_majority = ls.projects.create(
            title=PROJECT_TITLE_NO_MAJORITY,
            label_config=LABELING_CONFIG_NO_MAJORITY,
            description='Review Vietnamese dialect-to-English translations. No winner found, choose best or re-translate.',
        )
        ls.projects.import_tasks(id=proj_no_majority.id, request=tasks_no_majority)
        print(f'Project No Majority URL: {LABEL_STUDIO_URL}/projects/{proj_no_majority.id} (Tasks: {len(tasks_no_majority)})')


if __name__ == '__main__':
    main()
