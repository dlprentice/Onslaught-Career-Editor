/* address: 0x0054e160 */
/* name: CDXMeshVB__Load */
/* signature: undefined CDXMeshVB__Load(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXMeshVB__Load(undefined4 *param_1,void *param_2,int param_3)

{
  char cVar1;
  int iVar2;
  int arg6;
  void *this;
  int iVar3;
  char *pcVar4;
  undefined4 *puVar5;
  uint uVar6;
  uint uVar7;
  int unaff_EBX;
  int unaff_ESI;
  char *pcVar8;
  int unaff_EDI;
  char *pcVar9;
  int iVar10;
  int *piVar11;
  int local_8;
  undefined4 local_4;

  this = param_2;
  _DAT_009c63a4 = 0x2000000;
  _DAT_009c63a8 = 0x200;
  iVar3 = CWorld__Helper_004239b0((int)param_2);
  local_8 = param_1[1];
  iVar2 = param_1[0x43];
  local_4 = *param_1;
  CMeshPart__Helper_00423910((uint)this);
  CMeshPart__Helper_00423910((uint)this);
  puVar5 = param_1 + 2;
  param_2 = (void *)0x40;
  do {
    if ((void *)*puVar5 != (void *)0x0) {
      OID__FreeObject((void *)*puVar5);
      *puVar5 = 0;
    }
    puVar5 = puVar5 + 1;
    param_2 = (void *)((int)param_2 + -1);
  } while (param_2 != (void *)0x0);
  CMeshPart__Helper_00423960(this,(int)param_1,0x128,1,unaff_EDI);
  param_1[1] = local_8;
  param_1[0x43] = iVar2;
  param_1[0x48] = iVar3;
  pcVar8 = (char *)(*(int *)((int)this + 4) + 0x2c);
  uVar6 = 0xffffffff;
  pcVar4 = pcVar8;
  do {
    if (uVar6 == 0) break;
    uVar6 = uVar6 - 1;
    cVar1 = *pcVar4;
    pcVar4 = pcVar4 + 1;
  } while (cVar1 != '\0');
  pcVar4 = (char *)OID__AllocObject(~uVar6,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x6ce);
  uVar6 = 0xffffffff;
  param_1[0x49] = pcVar4;
  do {
    pcVar9 = pcVar8;
    if (uVar6 == 0) break;
    uVar6 = uVar6 - 1;
    pcVar9 = pcVar8 + 1;
    cVar1 = *pcVar8;
    pcVar8 = pcVar9;
  } while (cVar1 != '\0');
  uVar6 = ~uVar6;
  pcVar8 = pcVar9 + -uVar6;
  for (uVar7 = uVar6 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
    *(undefined4 *)pcVar4 = *(undefined4 *)pcVar8;
    pcVar8 = pcVar8 + 4;
    pcVar4 = pcVar4 + 4;
  }
  for (uVar6 = uVar6 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
    *pcVar4 = *pcVar8;
    pcVar8 = pcVar8 + 1;
    pcVar4 = pcVar4 + 1;
  }
  iVar3 = 0;
  *param_1 = local_4;
  if (0 < (int)param_1[0x42]) {
    do {
      puVar5 = (undefined4 *)
               OID__AllocObject(0x3c,0x3a,s_C__dev_ONSLAUGHT2_DXMeshVB_cpp_00651244,0x6dc);
      if (puVar5 == (undefined4 *)0x0) {
        puVar5 = (undefined4 *)0x0;
      }
      else {
        *puVar5 = 0;
        puVar5[1] = 0;
      }
      param_1[iVar3 + 2] = puVar5;
      CMeshPart__Helper_00423910((uint)this);
      CMeshPart__Helper_00423960(this,param_1[iVar3 + 2] + 8,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,param_1[iVar3 + 2] + 0xc,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,param_1[iVar3 + 2] + 0x10,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,param_1[iVar3 + 2] + 0x14,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,param_1[iVar3 + 2] + 0x18,4,1,unaff_EDI);
      CMeshPart__Helper_00423960(this,param_1[iVar3 + 2] + 0x1c,4,1,unaff_EDI);
      CMeshPart__Helper_00423910((uint)this);
      iVar10 = 8;
      if ((DAT_00854e6c != '\0') && (param_3 != 0)) {
        iVar10 = 0x18;
      }
      CEngine__DeviceCall6C
                (&DAT_00855bb0,*(int *)(param_1[iVar3 + 2] + 0xc),iVar10,0x65,1,
                 param_1[iVar3 + 2] + 4);
      DebugTrace((char *)&DAT_009c3df0);
      piVar11 = *(int **)(param_1[iVar3 + 2] + 4);
      (**(code **)(*piVar11 + 0x2c))(piVar11,0,0,&param_2,0);
      CMeshPart__Helper_00423960(this,unaff_EBX,2,*(int *)(param_1[iVar3 + 2] + 0x10),(int)piVar11);
      (**(code **)(**(int **)(param_1[iVar3 + 2] + 4) + 0x30))(*(int **)(param_1[iVar3 + 2] + 4));
      CMeshPart__Helper_00423910((uint)this);
      arg6 = param_1[2];
      if (iVar3 == 0) {
        CEngine__DeviceCall68_CheckError
                  (&DAT_00855bb0,*(int *)(arg6 + 8),iVar10,param_1[0x46],1,arg6);
        DebugTrace((char *)&DAT_009c3df0);
        piVar11 = *(int **)param_1[2];
        (**(code **)(*piVar11 + 0x2c))(piVar11,0,0,&local_4,0);
        CMeshPart__Helper_00423960
                  (this,unaff_ESI,param_1[0x45],*(int *)(param_1[2] + 0x14),(int)piVar11);
        (**(code **)(**(int **)param_1[2] + 0x30))(*(int **)param_1[2]);
      }
      else {
        *(undefined4 *)(param_1[iVar3 + 2] + 8) = *(undefined4 *)(arg6 + 8);
        *(undefined4 *)param_1[iVar3 + 2] = *(undefined4 *)param_1[2];
        *(undefined4 *)(param_1[iVar3 + 2] + 0x14) = *(undefined4 *)(param_1[2] + 0x14);
        CUnitAI__Unk_00423990(this);
      }
      CMeshPart__Helper_00423910((uint)this);
      iVar10 = 0x20;
      do {
        CMeshPart__Helper_00423960(this,(int)&local_8,4,1,unaff_EDI);
        if (local_8 == -1) {
          *(undefined4 *)(iVar10 + param_1[iVar3 + 2]) = 0;
        }
        else {
          *(int *)(iVar10 + param_1[iVar3 + 2]) = **(int **)(iVar2 + 0x128) + local_8 * 0x24;
        }
        iVar10 = iVar10 + 4;
      } while (iVar10 < 0x38);
      iVar3 = iVar3 + 1;
    } while (iVar3 < (int)param_1[0x42]);
  }
  return;
}
