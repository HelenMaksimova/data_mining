xpath_main_selectors = {
    'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    'vacancy': '//div[@class="vacancy-serp"]//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    'company_name': '//div[@class="vacancy-company__details"]//a[@class="vacancy-company-name"]//text()',
    'vacancy_title': '//div[@class="vacancy-title"]//h1[@data-qa="vacancy-title"]//text()'
}

xpath_vacancy_selectors = (
    {
        'field_name': 'salary',
        'xpath': '//div[@class="vacancy-title"]//p[contains(@class, "vacancy-salary")]//text()'
    },
    {
        'field_name': 'description',
        'xpath': '//div[@data-qa="vacancy-description"]//text()'
    },

    {
        'field_name': 'skills',
        'xpath': '//div[@class="bloko-tag-list"]//div[contains(@data-qa, "skills-element")]//text()'
    },
    {
        'field_name': 'company_url',
        'xpath': '//div[@class="vacancy-company__details"]//a[@class="vacancy-company-name"]/@href'
    }
)

xpath_company_selectors = (
    {
        'field_name': 'description',
        'xpath': '//div[@class="company-description"]//text()'
    },
    {
        'field_name': 'description',
        'xpath': '//div[@class="tmpl_hh_wrapper"]//text()'
    },
    {
        'field_name': 'link',
        'xpath': '//div[@class="employer-sidebar-content"]//a[@data-qa="sidebar-company-site"]/@href'
    },
    {
        'field_name': 'activity_areas',
        'xpath': '//div[@class="employer-sidebar-block"]/p/text()'
    }
)
