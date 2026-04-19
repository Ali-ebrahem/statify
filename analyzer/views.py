import pandas as pd
import io
import plotly.express as px
from django.shortcuts import render
from .forms import DatasetUploadForm


def home(request):
    return render(request, 'home.html')


def upload_dataset(request):
    form = DatasetUploadForm()
    table_html = None
    error_message = None
    domain = None
    columns = []
    row_count = 0

    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['file']
            domain = form.cleaned_data['domain']
            file_name = uploaded_file.name.lower()

            try:
                if file_name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = None
                    error_message = 'Unsupported file type.'

                if df is not None:
                    row_count = len(df)
                    columns = list(df.columns)

                    request.session['data'] = df.to_json()
                    request.session['domain'] = domain

                    table_html = df.head(20).to_html(
                        classes='table table-striped table-bordered',
                        index=False
                    )

            except Exception as e:
                error_message = f'Error: {str(e)}'

    return render(request, 'upload.html', {
        'form': form,
        'table_html': table_html,
        'error_message': error_message,
        'domain': domain,
        'columns': columns,
        'row_count': row_count,
    })


def dashboard(request):
    data_json = request.session.get('data')
    domain = request.session.get('domain')

    mean_value = None
    max_value = None
    min_value = None
    count_value = None
    chart_div = None
    insight_text = None   # 🔥 الجديد

    if data_json:
        df = pd.read_json(io.StringIO(data_json))
        numeric_df = df.select_dtypes(include='number')

        if not numeric_df.empty:
            mean_value = round(numeric_df.mean().mean(), 2)
            max_value = round(numeric_df.max().max(), 2)
            min_value = round(numeric_df.min().min(), 2)
            count_value = len(df)

            # 🔥 Chart
            first_col = numeric_df.columns[0]
            fig = px.line(df, x=df.index, y=first_col)
            fig.update_layout(template="plotly_dark")
            chart_div = fig.to_html(full_html=False)

            # 🔥 Insight Logic (بسيط ومفهوم)
            data_range = max_value - min_value

            if data_range < 20:
                variation = "low variation"
            elif data_range < 100:
                variation = "moderate variation"
            else:
                variation = "high variation"

            if mean_value < (min_value + max_value) / 2:
                distribution = "slightly skewed toward lower values"
            else:
                distribution = "slightly skewed toward higher values"

            insight_text = (
                f"The dataset contains {count_value} records with {variation}. "
                f"Values range from {min_value} to {max_value}, "
                f"and the distribution is {distribution}."
            )

    return render(request, 'dashboard.html', {
        'mean': mean_value,
        'max': max_value,
        'min': min_value,
        'count': count_value,
        'domain': domain,
        'chart': chart_div,
        'insight': insight_text,   # 🔥 الجديد
    })