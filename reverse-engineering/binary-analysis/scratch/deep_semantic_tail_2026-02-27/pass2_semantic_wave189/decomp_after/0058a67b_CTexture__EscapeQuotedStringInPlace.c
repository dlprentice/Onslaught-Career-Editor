/* address: 0x0058a67b */
/* name: CTexture__EscapeQuotedStringInPlace */
/* signature: void __stdcall CTexture__EscapeQuotedStringInPlace(void * param_1, int param_2, int param_3) */


void CTexture__EscapeQuotedStringInPlace(void *param_1,int param_2,int param_3)

{
  bool bVar1;
  bool bVar2;
  int iVar3;

  iVar3 = 0;
  bVar1 = false;
  bVar2 = false;
  for (; param_2 != 0; param_2 = param_2 + -1) {
    if (*(char *)param_1 == '\"') {
      if (param_3 != 0) {
        *(undefined1 *)(iVar3 + param_3) = 0x5c;
      }
      iVar3 = iVar3 + 1;
      if (!bVar1) {
        bVar2 = !bVar2;
      }
    }
    bVar1 = false;
    if ((bVar2) && (*(char *)param_1 == '\\')) {
      if (param_3 != 0) {
        *(undefined1 *)(iVar3 + param_3) = 0x5c;
      }
      iVar3 = iVar3 + 1;
      bVar1 = true;
    }
    if (param_3 != 0) {
      *(char *)(iVar3 + param_3) = *(char *)param_1;
    }
    iVar3 = iVar3 + 1;
    param_1 = (void *)((int)param_1 + 1);
  }
  return;
}
