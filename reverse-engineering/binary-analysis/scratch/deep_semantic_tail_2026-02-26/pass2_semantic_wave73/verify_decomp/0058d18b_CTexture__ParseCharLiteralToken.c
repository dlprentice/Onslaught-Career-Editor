/* address: 0x0058d18b */
/* name: CTexture__ParseCharLiteralToken */
/* signature: char * __thiscall CTexture__ParseCharLiteralToken(void * this, void * param_1, void * param_2, void * param_3) */


char * __thiscall
CTexture__ParseCharLiteralToken(void *this,void *param_1,void *param_2,void *param_3)

{
  int iVar1;
  char *pcVar2;
  void *unaff_EDI;

  if ((param_1 < *(void **)((int)this + 4)) && (*(char *)param_1 == '\'')) {
    iVar1 = CTexture__Helper_0058cef2(this,(int)param_1 + 1,param_2,unaff_EDI);
    if ((iVar1 != 0) &&
       ((pcVar2 = (char *)((int)param_1 + 1 + iVar1), pcVar2 < *(char **)((int)this + 4) &&
        (*pcVar2 == '\'')))) {
      return pcVar2 + (1 - (int)param_1);
    }
  }
  return (char *)0x0;
}
