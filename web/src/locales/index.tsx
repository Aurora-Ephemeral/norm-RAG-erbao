import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zh from './zh'
import en from './en'

const resources = {
  zh: {
    translation: zh
  },
  en: {
    translation: en
  }
}

i18n.use(initReactI18next).init({
    resources,
    lng: 'zh', // 默认语言
    fallbackLng: 'zh', // 如果当前语言没有翻译，则使用默认语言
    interpolation: {
      escapeValue: false // react already safes from xss
    }
});

export default i18n;