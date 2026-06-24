/* address: 0x004176c0 */
/* name: CThing__InitRenderThingFromInitMeshName */
/* signature: void __thiscall CThing__InitRenderThingFromInitMeshName(void * this, int param_1, int param_2) */


void __thiscall CThing__InitRenderThingFromInitMeshName(void *this,int param_1,int param_2)

{
  char cVar1;
  void *obj;
  int *piVar2;
  void *obj_00;
  uint uVar3;
  uint uVar4;
  char *pcVar5;
  int iVar6;
  char *pcVar7;
  char *pcVar8;
  char *pcVar9;
  undefined4 uVar10;
  char local_5b8 [256];
  char local_4b8 [256];
  undefined1 local_3b8;
  undefined1 local_2b8;
  int local_1b8;
  undefined4 local_1ac;
  undefined4 local_1a8;
  void *local_1a4;
  int local_1a0;
  char local_19c [400];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d154b;
  pvStack_c = ExceptionList;
  local_1b8 = 0;
  local_5b8[0] = '\0';
  local_4b8[0] = '\0';
  local_3b8 = 0;
  local_2b8 = 0;
  local_1ac = 0;
  local_1a8 = 0;
  local_1a4 = (void *)0x0;
  local_1a0 = 0;
  local_4 = 0;
  if (this != (void *)0x0) {
    local_1b8 = (int)this + 8;
  }
  ExceptionList = &pvStack_c;
  sprintf(local_19c,s__s_msh_00623b6c);
  uVar3 = 0xffffffff;
  pcVar7 = local_19c;
  do {
    pcVar5 = pcVar7;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar5 = pcVar7 + 1;
    cVar1 = *pcVar7;
    pcVar7 = pcVar5;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar7 = local_19c;
  pcVar5 = pcVar5 + -uVar3;
  pcVar9 = local_5b8;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar9 = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    pcVar9 = pcVar9 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar9 = *pcVar5;
    pcVar5 = pcVar5 + 1;
    pcVar9 = pcVar9 + 1;
  }
  uVar10 = *(undefined4 *)(*(int *)(param_1 + 0x3bc) + 0x30);
  pcVar9 = s__s_msh_00623b6c;
  sprintf(pcVar7,s__s_msh_00623b6c);
  uVar3 = 0xffffffff;
  pcVar5 = local_19c;
  do {
    pcVar8 = pcVar5;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar8 = pcVar5 + 1;
    cVar1 = *pcVar5;
    pcVar5 = pcVar8;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar5 = pcVar8 + -uVar3;
  pcVar8 = local_4b8;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar8 = *(undefined4 *)pcVar5;
    pcVar5 = pcVar5 + 4;
    pcVar8 = pcVar8 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar8 = *pcVar5;
    pcVar5 = pcVar5 + 1;
    pcVar8 = pcVar8 + 1;
  }
  piVar2 = (int *)PCRTID__CreateObject(4,pcVar7,pcVar9,uVar10);
  *(int **)((int)this + 0x30) = piVar2;
  if (piVar2 != (int *)0x0) {
    (**(code **)(*piVar2 + 4))(local_5b8);
  }
  iVar6 = 0;
  local_4 = 0xffffffff;
  obj_00 = local_1a4;
  if (0 < local_1a0) {
    do {
      obj = *(void **)((int)obj_00 + iVar6 * 4);
      if (obj != (void *)0x0) {
        OID__FreeObject(obj);
        *(undefined4 *)((int)local_1a4 + iVar6 * 4) = 0;
        obj_00 = local_1a4;
      }
      iVar6 = iVar6 + 1;
    } while (iVar6 < local_1a0);
  }
  if (obj_00 != (void *)0x0) {
    OID__FreeObject(obj_00);
  }
  ExceptionList = pvStack_c;
  return;
}
