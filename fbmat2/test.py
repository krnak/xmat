from selenium import webdriver
webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36'
driver = webdriver.PhantomJS()
driver.get("https://m.facebook.com")
driver.find_element_by_id('m_login_email').send_keys('epfs@seznam.cz')
driver.find_element_by_name('pass').send_keys('fekalfekalfekal')
driver.find_element_by_name('login').click()
driver.save_screenshot("C:/Users/HP/Desktop/now.png")
driver.get('https://m.facebook.com/groups/1942075575810809/')
driver.quit()