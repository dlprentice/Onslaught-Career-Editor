/* address: 0x0046b950 */
/* name: CFEPMultiplayerStart__Helper_0046b950 */
/* signature: void __thiscall CFEPMultiplayerStart__Helper_0046b950(void * this, int param_1, void * param_2) */


void __thiscall CFEPMultiplayerStart__Helper_0046b950(void *this,int param_1,void *param_2)

{
  char cVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  undefined4 *puVar6;
  char *pcVar7;
  undefined4 *puVar8;
  char *pcVar9;
  float10 fVar10;
  char local_42c [1024];
  void *local_2c;
  undefined4 local_10;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d276b;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  *(undefined4 *)((int)this + 4) = *(undefined4 *)param_1;
  *(undefined4 *)((int)this + 8) = *(undefined4 *)(param_1 + 4);
  *(undefined4 *)((int)this + 0xc) = *(undefined4 *)(param_1 + 8);
  *(undefined4 *)((int)this + 0x10) = *(undefined4 *)(param_1 + 0xc);
  puVar6 = (undefined4 *)(param_1 + 0x10);
  puVar8 = (undefined4 *)((int)this + 0x14);
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *puVar8 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar8 = puVar8 + 1;
  }
  eh_vector_constructor_iterator
            (local_42c,0x41c,1,CResourceDescriptor__ctor,CResourceDescriptor__dtor);
  local_10 = 1;
  uVar4 = 0xffffffff;
  pcVar7 = (char *)(param_1 + 0x40);
  do {
    pcVar9 = pcVar7;
    if (uVar4 == 0) break;
    uVar4 = uVar4 - 1;
    pcVar9 = pcVar7 + 1;
    cVar1 = *pcVar7;
    pcVar7 = pcVar9;
  } while (cVar1 != '\0');
  uVar4 = ~uVar4;
  pcVar7 = pcVar9 + -uVar4;
  pcVar9 = local_42c;
  local_2c = this;
  for (uVar5 = uVar4 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
    *(undefined4 *)pcVar9 = *(undefined4 *)pcVar7;
    pcVar7 = pcVar7 + 4;
    pcVar9 = pcVar9 + 4;
  }
  local_4 = 0;
  for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
    *pcVar9 = *pcVar7;
    pcVar7 = pcVar7 + 1;
    pcVar9 = pcVar9 + 1;
  }
  piVar2 = (int *)PCRTID__CreateObject(1);
  *(int **)((int)this + 0x58) = piVar2;
  if (piVar2 == (int *)0x0) {
    *(undefined4 *)((int)this + 0x48) = 0;
    *(undefined4 *)((int)this + 0x4c) = 0;
    *(undefined4 *)((int)this + 0x44) = 0;
  }
  else {
    (**(code **)(*piVar2 + 4))(local_42c);
    fVar10 = (float10)(**(code **)(**(int **)((int)this + 0x58) + 0x38))(1,(int)this + 0x44);
    *(float *)((int)this + 0x48) = (float)fVar10;
    *(undefined4 *)((int)this + 0x4c) = 0;
  }
  *(undefined4 *)((int)this + 0x50) = 1;
  *(undefined4 *)((int)this + 0x54) = 200;
  local_4 = 0xffffffff;
  CFastVB__Unk_0055db0a((int)local_42c,0x41c,1,CResourceDescriptor__dtor);
  ExceptionList = pvStack_c;
  return;
}
