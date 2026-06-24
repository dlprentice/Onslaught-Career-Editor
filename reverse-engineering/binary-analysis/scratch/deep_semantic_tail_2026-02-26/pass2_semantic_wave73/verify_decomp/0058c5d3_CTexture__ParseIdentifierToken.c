/* address: 0x0058c5d3 */
/* name: CTexture__ParseIdentifierToken */
/* signature: uint __thiscall CTexture__ParseIdentifierToken(void * this, void * param_1, void * param_2, void * param_3) */


uint __thiscall CTexture__ParseIdentifierToken(void *this,void *param_1,void *param_2,void *param_3)

{
  void *pvVar1;
  void *this_00;
  uint uVar2;
  undefined4 *extraout_EAX;
  uint uVar3;
  int unaff_EDI;
  char *pcVar4;
  undefined4 *puVar5;

  if (param_1 < *(void **)((int)this + 4)) {
    this_00 = (void *)(int)*(char *)param_1;
    uVar2 = CTexture__Helper_0056a05b(this,this_00,unaff_EDI);
    pcVar4 = param_1;
    if ((uVar2 != 0) || (*(char *)param_1 == '_')) {
      do {
        pcVar4 = pcVar4 + 1;
        if (*(char **)((int)this + 4) <= pcVar4) break;
        pvVar1 = (void *)(int)*pcVar4;
        uVar2 = CTexture__Unk_0056a106(this_00,(void *)(int)*pcVar4,unaff_EDI);
        this_00 = pvVar1;
      } while ((uVar2 != 0) || (*pcVar4 == '_'));
      uVar2 = (int)pcVar4 - (int)param_1;
      CTexture__Helper_0058c107(*(void **)((int)this + 0x2c),(void *)(uVar2 + 1),unaff_EDI);
      if (extraout_EAX != (undefined4 *)0x0) {
        puVar5 = extraout_EAX;
        for (uVar3 = uVar2 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
          *puVar5 = *(undefined4 *)param_1;
          param_1 = (undefined4 *)((int)param_1 + 4);
          puVar5 = puVar5 + 1;
        }
        for (uVar3 = uVar2 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
          *(undefined1 *)puVar5 = *(undefined1 *)param_1;
          param_1 = (undefined4 *)((int)param_1 + 1);
          puVar5 = (undefined4 *)((int)puVar5 + 1);
        }
        *(undefined1 *)((int)extraout_EAX + uVar2) = 0;
        *(undefined4 **)param_2 = extraout_EAX;
        return uVar2;
      }
    }
  }
  return 0;
}
