" vimscript to fix txt rules docs from WotC website
" run with: vim -c "source format_rulesdoc.vim" filename

e ++enc=cp1252
w ++enc=utf-8 %
e
set ff=unix
%s/\s\+$//g
wq
