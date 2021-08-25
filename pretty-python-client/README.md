Pretty-python-client
=========
Для использования расширения в качестве клиента для `pretty-python-server` достаточно следовать четырем простым правилам:
1) Запустите команду для установки nbextensions

   `pip install jupyter_contrib_nbextensions && jupyter contrib nbextension install`

2) Найдите директорию с nbextensions, например так:

    `pip show jupyter_contrib_nbextensions`
   
3) Переместите `pretty-python-client` в директорию с другими nbextensions.
4) Запустите команду `jupyter contrib nbextension install` снова для того, чтобы
`pretty-python-client` появился в списке расширений Jupyter Notebook

Готово! Осталось только запустить Jupyter и поставить галочку у этого расширения во вкладке Nbextensions стартовой страницы.