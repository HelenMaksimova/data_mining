main_selectors = {
    'js_script_data': '//div[@class="js-initial"]/@data-state'
}

flat_selectors = (
    {
        'field_name': 'title',
        'xpath': '//span[@class="title-info-title-text"]//text()'
    },
    {
        'field_name': 'price',
        'xpath': '//span[@itemprop="price"]//text()'
    },
    {
        'field_name': 'address',
        'xpath': '//span[@class="item-address__string"]//text()'
    },
    {
        'field_name': 'characteristics',
        'xpath': '//ul[@class="item-params-list"]/li//text()'
    },
    {
        'field_name': 'seller_url',
        'xpath': '//div[contains(@class, "seller-info-name")]//a/@href'
    }
)
