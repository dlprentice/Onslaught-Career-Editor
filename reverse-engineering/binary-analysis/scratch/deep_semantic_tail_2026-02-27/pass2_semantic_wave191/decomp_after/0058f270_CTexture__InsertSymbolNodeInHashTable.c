/* address: 0x0058f270 */
/* name: CTexture__InsertSymbolNodeInHashTable */
/* signature: int __thiscall CTexture__InsertSymbolNodeInHashTable(void * this, int param_1, void * param_2, int param_3, int param_4) */


int __thiscall
CTexture__InsertSymbolNodeInHashTable(void *this,int param_1,void *param_2,int param_3,int param_4)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  char *pcVar4;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  undefined4 *puVar5;
  uint uVar6;

  uVar3 = CTexture__HashIdentifierMod7((void *)param_1);
  pcVar4 = (char *)param_1;
  do {
    cVar1 = *pcVar4;
    pcVar4 = pcVar4 + 1;
  } while (cVar1 != '\0');
  pcVar4 = pcVar4 + (1 - (param_1 + 1));
  OID__AllocObject_DefaultTag_00662b2c((int)pcVar4);
  if (extraout_EAX != (undefined4 *)0x0) {
    puVar5 = extraout_EAX;
    for (uVar6 = (uint)pcVar4 >> 2; uVar6 != 0; uVar6 = uVar6 - 1) {
      *puVar5 = *(undefined4 *)param_1;
      param_1 = (int)(param_1 + 4);
      puVar5 = puVar5 + 1;
    }
    for (uVar6 = (uint)pcVar4 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
      *(undefined1 *)puVar5 = *(undefined1 *)param_1;
      param_1 = (int)(param_1 + 1);
      puVar5 = (undefined4 *)((int)puVar5 + 1);
    }
    OID__AllocObject_DefaultTag_00662b2c(0x24);
    if (extraout_EAX_00 == (undefined4 *)0x0) {
      puVar5 = (undefined4 *)0x0;
    }
    else {
      uVar2 = *(undefined4 *)((int)this + uVar3 * 4);
      extraout_EAX_00[3] = 0;
      extraout_EAX_00[1] = param_2;
      *extraout_EAX_00 = extraout_EAX;
      extraout_EAX_00[2] = param_3;
      extraout_EAX_00[8] = uVar2;
      puVar5 = extraout_EAX_00;
    }
    if (puVar5 != (undefined4 *)0x0) {
      *(undefined4 **)((int)this + uVar3 * 4) = puVar5;
      return 0;
    }
  }
  return -0x7ff8fff2;
}
