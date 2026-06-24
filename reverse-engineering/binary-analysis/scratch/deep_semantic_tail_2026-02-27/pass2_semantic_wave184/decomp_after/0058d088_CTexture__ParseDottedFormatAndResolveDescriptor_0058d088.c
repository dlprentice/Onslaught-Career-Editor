/* address: 0x0058d088 */
/* name: CTexture__ParseDottedFormatAndResolveDescriptor_0058d088 */
/* signature: char * __thiscall CTexture__ParseDottedFormatAndResolveDescriptor_0058d088(void * this, void * param_1, void * param_2, void * param_3) */


char * __thiscall
CTexture__ParseDottedFormatAndResolveDescriptor_0058d088
          (void *this,void *param_1,void *param_2,void *param_3)

{
  void *this_00;
  uint uVar1;
  int iVar2;
  undefined4 *puVar3;
  void *unaff_EDI;
  char *pcVar4;
  undefined4 *puVar5;
  undefined4 local_30;
  char acStack_2c [28];
  undefined1 local_10 [4];
  undefined4 local_c;

  puVar3 = param_1;
  if ((*(byte *)((int)this + 0x28) & 2) == 0) {
    return (char *)0x0;
  }
  pcVar4 = (char *)((int)param_1 + 1);
  if (pcVar4 < *(char **)((int)this + 4)) {
    this_00 = (void *)(int)*(char *)param_1;
    uVar1 = CTexture__Helper_0056a05b(this,this_00,(int)unaff_EDI);
    if ((((uVar1 != 0) &&
         (uVar1 = CTexture__Helper_0056a05b(this_00,(void *)(int)*pcVar4,(int)unaff_EDI), uVar1 != 0
         )) && ((char *)((int)puVar3 + 2U) < *(char **)((int)this + 4))) &&
       (*(char *)((int)puVar3 + 2U) == '.')) {
      iVar2 = CTexture__Helper_0058ce51(this,(void *)((int)puVar3 + 3),&param_1,unaff_EDI);
      if (((iVar2 != 0) && (param_1 < (void *)0x100)) &&
         ((pcVar4 = (char *)((int)puVar3 + 3 + iVar2), pcVar4 < *(char **)((int)this + 4) &&
          (*pcVar4 == '.')))) {
        pcVar4 = pcVar4 + 1;
        uVar1 = CTexture__Helper_0058ce51(this,pcVar4,&param_1,unaff_EDI);
        if (uVar1 == 0) {
          uVar1 = CTexture__ParseIdentifierToken(this,pcVar4,&param_1,unaff_EDI);
          if (uVar1 == 0) {
            return (char *)0x0;
          }
          param_1 = (void *)0x0;
        }
        if ((param_1 < (void *)0x100) &&
           (pcVar4 = pcVar4 + (uVar1 - (int)puVar3), pcVar4 < (char *)0x20)) {
          puVar5 = &local_30;
          for (uVar1 = (uint)pcVar4 >> 2; uVar1 != 0; uVar1 = uVar1 - 1) {
            *puVar5 = *puVar3;
            puVar3 = puVar3 + 1;
            puVar5 = puVar5 + 1;
          }
          for (uVar1 = (uint)pcVar4 & 3; uVar1 != 0; uVar1 = uVar1 - 1) {
            *(undefined1 *)puVar5 = *(undefined1 *)puVar3;
            puVar3 = (undefined4 *)((int)puVar3 + 1);
            puVar5 = (undefined4 *)((int)puVar5 + 1);
          }
          *(char *)((int)&local_30 + (int)pcVar4) = '\0';
          iVar2 = CDXTexture__LookupNamedFormatDescriptor(&local_30,1,local_10);
          if (-1 < iVar2) {
            *(undefined4 *)param_2 = local_c;
            return pcVar4;
          }
        }
      }
    }
  }
  return (char *)0x0;
}
