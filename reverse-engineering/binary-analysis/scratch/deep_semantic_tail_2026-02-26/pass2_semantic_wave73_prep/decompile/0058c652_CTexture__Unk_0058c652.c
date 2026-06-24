/* address: 0x0058c652 */
/* name: CTexture__Unk_0058c652 */
/* signature: int __thiscall CTexture__Unk_0058c652(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Unk_0058c652(void *this,int param_1,void *param_2,void *param_3)

{
  char *pcVar1;
  char cVar2;
  char cVar3;

  *(undefined4 *)param_2 = 0;
  *(undefined1 *)param_2 = *(undefined1 *)param_1;
  pcVar1 = (char *)(param_1 + 1);
  if (*(char **)((int)this + 4) <= pcVar1) {
    return 1;
  }
  cVar2 = *(char *)param_1;
  if ((cVar2 == '#') && ((cVar3 = *pcVar1, cVar3 == '#' || (cVar3 == '@')))) {
    *(char *)((int)param_2 + 1) = cVar3;
    return 2;
  }
  cVar3 = *pcVar1;
  if (cVar2 != cVar3) {
    if (cVar3 == '=') {
      if (cVar2 < '0') {
        if (((cVar2 != '/') && (cVar2 != '!')) &&
           ((cVar2 < '%' || (('&' < cVar2 && ((cVar2 < '*' || (('+' < cVar2 && (cVar2 != '-'))))))))
           )) {
          return 1;
        }
      }
      else if ((((cVar2 != '<') && (cVar2 != '>')) && (cVar2 != '^')) && (cVar2 != '|')) {
        return 1;
      }
      *(undefined1 *)((int)param_2 + 1) = 0x3d;
      return 2;
    }
    if (cVar2 != '-') {
      return 1;
    }
    if (cVar3 == '>') {
      *(undefined1 *)((int)param_2 + 1) = 0x3e;
      return 2;
    }
    return 1;
  }
  if (cVar2 < ';') {
    if ((((cVar2 != ':') && (cVar2 != '&')) && (cVar2 != '+')) && (cVar2 != '-')) {
      if (cVar2 != '.') {
        return 1;
      }
      pcVar1 = (char *)(param_1 + 2);
      if (pcVar1 < *(char **)((int)this + 4)) {
        if (*pcVar1 == '.') {
          *(char *)((int)param_2 + 1) = cVar3;
          *(char *)((int)param_2 + 2) = *pcVar1;
          return 3;
        }
        return 1;
      }
      return 1;
    }
  }
  else {
    if (cVar2 == '<') {
LAB_0058c6e1:
      *(char *)((int)param_2 + 1) = cVar3;
      if (*(char **)((int)this + 4) <= (char *)(param_1 + 2U)) {
        return 2;
      }
      if (*(char *)(param_1 + 2U) != '=') {
        return 2;
      }
      *(undefined1 *)((int)param_2 + 2) = 0x3d;
      return 3;
    }
    if (cVar2 != '=') {
      if (cVar2 == '>') goto LAB_0058c6e1;
      if (cVar2 != '|') {
        return 1;
      }
    }
  }
  *(char *)((int)param_2 + 1) = cVar3;
  return 2;
}
