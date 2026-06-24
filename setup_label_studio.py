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

INPUT_FILE = 'voting_results.csv'
PROJECT_TITLE = 'Dialect2English - Translation Review'

# ============================================================
# Labeling Config — 1 project duy nhất cho cả 2 loại task
#
# - task_info: banner hướng dẫn annotator (majority/no-majority)
# - winner_info: hiển thị winner nổi bật (majority) hoặc ẩn (no-majority)
# - 3 candidates luôn hiện để tham khảo
# - Choices: Accept, Reject, Choose A/B/C, Re-translate
# ============================================================
LABELING_CONFIG = '''<View>
  <Header value="Vietnamese (Standard)" size="2" />
  <Text name="standard" value="$standard" granularity="word" />

  <View style="margin:12px 0; padding:12px 16px; border-radius:6px; background:#fff3e0; border-left:4px solid #ff9800;">
    <Text name="task_info" value="$task_info" />
  </View>

  <View style="margin:8px 0; padding:12px 16px; border-radius:6px; background:#e8f5e9; border-left:4px solid #4caf50;">
    <Text name="winner_info" value="$winner_info" />
  </View>

  <View style="margin-top:12px; padding:12px; background:#fafafa; border:1px solid #e0e0e0; border-radius:6px;">
    <Header value="Candidate A" size="4" />
    <Text name="candidate_a" value="$candidate_A" />
  </View>

  <View style="margin-top:8px; padding:12px; background:#fafafa; border:1px solid #e0e0e0; border-radius:6px;">
    <Header value="Candidate B" size="4" />
    <Text name="candidate_b" value="$candidate_B" />
  </View>

  <View style="margin-top:8px; padding:12px; background:#fafafa; border:1px solid #e0e0e0; border-radius:6px;">
    <Header value="Candidate C" size="4" />
    <Text name="candidate_c" value="$candidate_C" />
  </View>

  <View style="margin-top:16px;">
    <Header value="Your Decision" size="3" />
    <Choices name="decision" toName="standard" choice="single" required="true">
      <Choice value="Accept" />
      <Choice value="Reject" />
      <Choice value="Choose A" />
      <Choice value="Choose B" />
      <Choice value="Choose C" />
      <Choice value="Re-translate" />
    </Choices>
  </View>

  <View style="margin-top:12px;">
    <Header value="New / Corrected Translation (if Reject or Re-translate)" size="4" />
    <TextArea name="new_translation" toName="standard"
              placeholder="Write your translation here..."
              maxSubmissions="1" editable="true" />
  </View>
</View>'''


def build_tasks(df):
    """Tạo danh sách tasks cho Label Studio."""
    tasks = []

    for _, row in df.iterrows():
        winner = row['winner'] if pd.notna(row['winner']) and row['winner'] != '' else None

        task_data = {
            'original_index': int(row['original_index']),
            'split_source': row['split_source'],
            'standard': row['standard'],
            'candidate_A': row['A'],
            'candidate_B': row['B'],
            'candidate_C': row['C'],
            'winner': winner if winner else 'None',
        }

        if winner:
            winner_text = row[winner]
            task_data['task_info'] = (
                f'MAJORITY — Winner: Candidate {winner}. '
                f'Please Accept or Reject the winner translation.'
            )
            task_data['winner_info'] = (
                f'Winner (Candidate {winner}): {winner_text}'
            )
        else:
            task_data['task_info'] = (
                'NO MAJORITY — 3 judges chose 3 different candidates. '
                'Please Choose the best (A/B/C) or Re-translate.'
            )
            task_data['winner_info'] = 'No winner — please review all candidates below.'

        tasks.append({'data': task_data})

    return tasks


def main():
    if not LABEL_STUDIO_API_KEY:
        print('ERROR: LABEL_STUDIO_API_KEY not found in .env')
        return

    # 1. Read data
    df = pd.read_csv(INPUT_FILE)
    majority_count = (df['winner'].notna() & (df['winner'] != '')).sum()
    no_majority_count = len(df) - majority_count
    print(f'Loaded {len(df)} samples (majority: {majority_count}, no majority: {no_majority_count})')

    # 2. Build tasks
    tasks = build_tasks(df)

    # 3. Connect & create project
    print(f'Connecting to {LABEL_STUDIO_URL}...')
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)

    print(f'Creating project: {PROJECT_TITLE}')
    project = ls.projects.create(
        title=PROJECT_TITLE,
        label_config=LABELING_CONFIG,
        description=(
            'Review Vietnamese dialect-to-English translations.\n'
            'MAJORITY tasks: Accept or Reject the winner translation.\n'
            'NO MAJORITY tasks: Choose the best candidate (A/B/C) or Re-translate.'
        ),
    )

    # 4. Import tasks
    print(f'Importing {len(tasks)} tasks...')
    ls.projects.import_tasks(id=project.id, request=tasks)

    print(f'\n{"="*55}')
    print(f'Project URL: {LABEL_STUDIO_URL}/projects/{project.id}')
    print(f'Tasks: {len(tasks)} ({majority_count} majority + {no_majority_count} no majority)')
    print(f'{"="*55}')


if __name__ == '__main__':
    main()
