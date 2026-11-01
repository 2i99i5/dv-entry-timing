# LinkedIn draft

## English — ready to copy

My wife's DV lottery entry was selected in DV-2024. I had submitted it on the very last day.

We had entered several times before. That year, I kept putting it off: work, photos, a slow website. It almost became another thing I hadn't found time to do.

Only after her selection did I learn two things: being selected does not guarantee a visa, and public CEAC data can shed light on interview scheduling and visa outcomes.

Then I noticed something that brought that last-minute submission back to mind: a similar late-entry peak appeared across several years.

So I compared the data, aligning each year by relative submission day.

Across the DV-2017–2025 snapshots I analyzed, the last two observed dates accounted for 11.5–16.9% of cases with at least one issued visa and a known submission-date field. For DV-2024, that was 3,645 out of 26,110 cases: 13.96%.

The biggest daily count was on the penultimate observed date in every one of those nine snapshots.

Tempting conclusion: submitting late helps.

But the denominator is missing. These data do not tell me how many people entered on each day. If many more entries arrive near the deadline, more eventual issued cases could come from those dates even with unchanged odds.

There is another limitation: submission dates are missing for many selected cases. Even the daily issuance shares I can calculate describe only the dated sample. I also treat CEAC's submitDate field as an entry-date proxy, not an independently verified definition.

The pattern is real in these snapshots. A late-entry advantage is not established.

This project started with a family memory and became a useful lesson in data analysis: a distribution among outcomes does not tell you the probability of an outcome.

I've put the code, figures, aggregate data and limitations here:
https://github.com/2i99i5/dv-entry-timing

Thanks to Xarthisius / DV Charts for making the underlying CEAC data available.

#DataAnalysis #DataVisualization #DiversityVisa

## Русский перевод

Анкета моей жены была отобрана в лотерее DV-2024. Я подал её в самый последний день.

До этого мы участвовали несколько раз. В тот год я всё откладывал: работа, фотографии, медленный сайт. Это чуть не стало ещё одним делом, на которое я так и не нашёл времени.

Только после отбора я узнал две вещи: отбор не гарантирует получения визы, а открытые данные CEAC позволяют узнать больше о назначении интервью и визовых исходах.

Потом я заметил то, что напомнило о нашей подаче в последний момент: похожий пик поздних заявок повторялся в нескольких годах.

Я сравнил данные, выровняв годы по относительному дню подачи.

В исследованных снимках DV-2017–2025 последние две наблюдаемые даты давали 11,5–16,9% кейсов с хотя бы одной выданной визой и известным полем даты подачи. Для DV-2024 это 3 645 из 26 110 кейсов: 13,96%.

Во всех девяти снимках самое высокое дневное количество приходилось на предпоследнюю наблюдаемую дату.

Соблазнительный вывод: поздняя подача помогает.

Но не хватает знаменателя. Эти данные не показывают, сколько людей подаёт заявки в каждый день. Если перед дедлайном приходит намного больше заявок, среди будущих выданных кейсов тоже может оказаться больше поздних — даже при неизменных шансах.

Есть и другое ограничение: у многих отобранных кейсов отсутствуют даты. Даже доступные дневные доли выдач описывают только выборку с датами. Поле submitDate из CEAC я также использую как приближение даты заявки, а не как независимо подтверждённое определение.

В этих снимках закономерность наблюдается. Преимущество поздней подачи не установлено.

Проект начался с семейного воспоминания и стал полезным уроком анализа данных: распределение среди исходов не показывает вероятность исхода.

Код, графики, агрегированные данные и ограничения:
https://github.com/2i99i5/dv-entry-timing

Спасибо Xarthisius / DV Charts за открытый доступ к исходным данным CEAC.

#DataAnalysis #DataVisualization #DiversityVisa

## Publication notes / Примечания

- Attach `figures/linkedin_last_two_days_en.png` for the concise finding, or `figures/all_years_all_en.png` for the full comparison.
- The repository URL is included. Do not publish the notes section.
- Source background: [official DV-2024 page](https://travel.state.gov/content/travel/en/us-visas/immigrate/diversity-visa-program-entry/dv-2024-selected-entrants.html), [DV Charts](https://dvcharts.xarthisius.xyz/).
- The post reports the wife's selection, not an unconfirmed visa outcome. / Пост сообщает об отборе анкеты жены, а не о неподтверждённой выдаче виз.
