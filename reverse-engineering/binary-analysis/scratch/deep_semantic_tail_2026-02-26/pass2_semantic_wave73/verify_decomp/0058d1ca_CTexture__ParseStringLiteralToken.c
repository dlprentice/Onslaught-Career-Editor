/* address: 0x0058d1ca */
/* name: CTexture__ParseStringLiteralToken */
/* signature: char * __thiscall CTexture__ParseStringLiteralToken(void * this, void * param_1, void * param_2, void * param_3) */


char * __thiscall
CTexture__ParseStringLiteralToken(void *this,void *param_1,void *param_2,void *param_3)

{
  char *pcVar1;
  char cVar2;
  char *pcVar3;
  undefined1 *extraout_EAX;
  char cVar4;
  char *pcVar5;
  undefined1 *puVar6;
  void *unaff_EDI;
  int iVar7;
  char *pcVar8;

  pcVar3 = *(char **)((int)this + 4);
  if (pcVar3 <= param_1) {
    return (char *)0x0;
  }
  if (*(char *)param_1 == '\"') {
    cVar4 = '\"';
  }
  else {
    if (*(char *)param_1 != '<') {
      return (char *)0x0;
    }
    if ((*(byte *)((int)this + 0x28) & 8) == 0) {
      return (char *)0x0;
    }
    cVar4 = '>';
  }
  pcVar1 = (char *)((int)param_1 + 1);
  for (pcVar5 = pcVar1; ((pcVar5 < pcVar3 && (cVar2 = *pcVar5, cVar4 != cVar2)) && (cVar2 != '\n'));
      pcVar5 = pcVar5 + 1) {
    if ((cVar2 == '\\') && ((*(byte *)((int)this + 0x28) & 4) == 0)) {
      pcVar5 = pcVar5 + 1;
    }
  }
  if (pcVar5 < pcVar3) {
    if (*pcVar5 != '\n') goto LAB_0058d253;
    pcVar8 = "string continues past end of line";
    iVar7 = 0x3ed;
  }
  else {
    pcVar8 = "string continues past end of file";
    iVar7 = 0x3ee;
    pcVar5 = pcVar3;
  }
  CTexture__Helper_0058c893(*(void **)((int)this + 0x30),(int)this + 8,iVar7,(int)pcVar8);
LAB_0058d253:
  CTexture__Helper_0058c107(*(void **)((int)this + 0x2c),pcVar5 + -(int)param_1,(int)unaff_EDI);
  if (extraout_EAX == (undefined1 *)0x0) {
    return (char *)0x0;
  }
  *(undefined1 **)param_2 = extraout_EAX;
  puVar6 = extraout_EAX;
  for (; pcVar1 < pcVar5; pcVar1 = pcVar1 + iVar7) {
    iVar7 = CTexture__Helper_0058cef2(this,(int)pcVar1,&param_2,unaff_EDI);
    *puVar6 = param_2._0_1_;
    puVar6 = puVar6 + 1;
  }
  *puVar6 = 0;
  return pcVar5 + -(int)param_1 + 1;
}
