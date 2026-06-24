/* address: 0x0055a420 */
/* name: CDXTrees__BuildTreeGeometry */
/* signature: undefined CDXTrees__BuildTreeGeometry(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXTrees__BuildTreeGeometry(int param_1)

{
  void *pvVar1;
  int *piVar2;
  float fVar3;
  float fVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int extraout_EAX;
  float *pfVar8;
  byte bVar9;
  undefined4 *puVar10;
  int iVar11;
  int unaff_EDI;
  int iVar12;
  double dVar13;
  float fStack_e4;
  short sStack_d4;
  short sStack_d2;
  short sStack_d0;
  short sStack_ce;
  short sStack_cc;
  short sStack_ca;
  int local_c8;
  int local_c4;
  short local_c0;
  short local_be;
  int local_bc;
  int local_b8;
  int local_b4;
  float local_b0;
  float local_ac;
  float fStack_a8;
  float fStack_9c;
  float fStack_98;
  float fStack_90;
  float fStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  float fStack_78;
  float fStack_74;
  undefined4 uStack_6c;
  float fStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  float fStack_54;
  float fStack_50;
  float fStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  float fStack_30;
  float fStack_2c;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d7e22;
  local_c = ExceptionList;
  pvVar1 = *(void **)(param_1 + 8);
  ExceptionList = &local_c;
  if (pvVar1 != (void *)0x0) {
    ExceptionList = &local_c;
    CVBufTexture__dtor();
    OID__FreeObject(pvVar1);
    *(undefined4 *)(param_1 + 8) = 0;
  }
  pvVar1 = *(void **)(param_1 + 0xc);
  if (pvVar1 != (void *)0x0) {
    CVBufTexture__dtor();
    OID__FreeObject(pvVar1);
    *(undefined4 *)(param_1 + 0xc) = 0;
  }
  *(undefined4 *)(param_1 + 0x10) = 0;
  local_c8 = OID__AllocObject(0x68,0x1f,s_C__dev_ONSLAUGHT2_DXTrees_cpp_006529b0,0x5e);
  local_4 = 0;
  if (local_c8 == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = CVBufTexture__CVBufTexture(0);
  }
  *(undefined4 *)(param_1 + 8) = uVar5;
  bVar9 = -(DAT_00854e6c != '\0') & 0x10;
  local_4 = 0xffffffff;
  CVBufTexture__SetVBFormat(0x152,bVar9,0x24,4,1);
  CVBufTexture__SetIBFormat(0x65,bVar9,2,1);
  CVBufTexture__SetPersist();
  local_c8 = OID__AllocObject(0x68,0x1f,s_C__dev_ONSLAUGHT2_DXTrees_cpp_006529b0,0x6a);
  local_4 = 1;
  if (local_c8 == 0) {
    uVar5 = 0;
  }
  else {
    uVar5 = CVBufTexture__CVBufTexture(0);
  }
  local_4 = 0xffffffff;
  *(undefined4 *)(param_1 + 0xc) = uVar5;
  CVBufTexture__SetVBFormat(0x152,bVar9,0x24,4,1);
  CVBufTexture__SetIBFormat(0x65,bVar9,2,1);
  CVBufTexture__SetPersist();
  local_c4 = 4;
  local_b0 = 0.0;
  do {
    iVar6 = (int)(0x40 / (longlong)(1 << (SUB41(local_b0,0) & 0x1f)));
    local_b4 = 0;
    local_c8 = iVar6;
    if (0 < iVar6) {
      do {
        local_b8 = 0;
        iVar12 = local_b4;
        do {
          iVar11 = local_b8;
          local_c0 = (short)iVar12;
          local_be = (short)local_b8;
          local_bc = local_c4;
          iVar7 = CMapWho__IsEntryInBounds(&local_c0);
          if (iVar7 != 0) {
            CCollisionSeekingRound__Helper_00491d80
                      (&DAT_00704200,
                       (void *)(*(int *)(DAT_00704290 + local_bc * 4) +
                               ((0x40 >> (4U - (char)local_bc & 0x1f)) * (int)local_be +
                               (int)local_c0) * 8),unaff_EDI);
            iVar7 = extraout_EAX;
            while (iVar7 != 0) {
              iVar6 = CMapWhoEntry__GetOwner();
              if ((*(uint *)(iVar6 + 0x34) & 0x2000000) != 0) {
                piVar2 = *(int **)(iVar6 + 0x30);
                pvVar1 = (void *)piVar2[6];
                (*(code *)**(undefined4 **)(iVar6 + 8))(&local_ac);
                pfVar8 = (float *)(**(code **)(*piVar2 + 0x10))();
                local_b0 = local_b0 + *pfVar8;
                fVar3 = local_ac + pfVar8[1];
                fVar4 = fStack_a8 + pfVar8[2];
                local_ac = fVar3;
                fStack_a8 = fVar4;
                iVar6 = (**(code **)(*(int *)(iVar6 + 8) + 0x6c))();
                if ((*(int *)((int)pvVar1 + 0x3c) == 0) ||
                   (puVar10 = (undefined4 *)(*(int *)((int)pvVar1 + 0x3c) + iVar6 * 0x18),
                   puVar10 == (undefined4 *)0x0)) {
                  *(undefined2 *)(piVar2 + 0xc) = 0xffff;
                }
                else {
                  uStack_80 = *puVar10;
                  uStack_7c = puVar10[2];
                  uStack_84 = 0xffffffff;
                  fStack_90 = -(float)puVar10[4];
                  fStack_8c = -(float)puVar10[5];
                  uStack_88 = 0;
                  uStack_5c = puVar10[1];
                  uStack_58 = puVar10[2];
                  uStack_60 = 0xffffffff;
                  uStack_6c = puVar10[4];
                  fStack_68 = -(float)puVar10[5];
                  uStack_64 = 0;
                  uStack_38 = *puVar10;
                  uStack_34 = puVar10[3];
                  uStack_3c = 0xffffffff;
                  fStack_48 = -(float)puVar10[4];
                  uStack_44 = puVar10[5];
                  uStack_40 = 0;
                  uStack_14 = puVar10[1];
                  uStack_10 = puVar10[3];
                  uStack_18 = 0xffffffff;
                  uStack_24 = puVar10[4];
                  uStack_20 = puVar10[5];
                  uStack_1c = 0;
                  fStack_9c = fVar3;
                  fStack_78 = fVar3;
                  fStack_54 = fVar3;
                  fStack_30 = fVar3;
                  sStack_d4 = CVBufTexture__AddVertices(&fStack_9c,4);
                  sStack_d2 = sStack_d4 + 1;
                  sStack_d0 = sStack_d4 + 2;
                  sStack_cc = sStack_d4 + 3;
                  sStack_ce = sStack_d0;
                  sStack_ca = sStack_d2;
                  CVBufTexture__AddIndices(&sStack_d4,6);
                  *(short *)(piVar2 + 0xc) = sStack_d4;
                  if (*(int *)((int)pvVar1 + 0x3c) == 0) {
                    puVar10 = (undefined4 *)0x0;
                  }
                  else {
                    puVar10 = (undefined4 *)(*(int *)((int)pvVar1 + 0x3c) + 0x60);
                  }
                  dVar13 = CIBuffer__Unk_00488aa0(pvVar1,(int)fVar4,unaff_EDI);
                  fStack_50 = (float)dVar13 * _DAT_005d8bec;
                  fStack_9c = fVar3 - fStack_50;
                  fStack_98 = fStack_e4 - fStack_50;
                  fStack_78 = fStack_50 + fVar3;
                  uStack_80 = *puVar10;
                  uStack_7c = puVar10[2];
                  uStack_84 = 0xffffffff;
                  fStack_50 = fStack_50 + fStack_e4;
                  uStack_5c = puVar10[1];
                  uStack_58 = puVar10[2];
                  uStack_60 = 0xffffffff;
                  uStack_38 = puVar10[1];
                  uStack_34 = puVar10[3];
                  uStack_3c = 0xffffffff;
                  uStack_14 = *puVar10;
                  uStack_10 = puVar10[3];
                  uStack_18 = 0xffffffff;
                  fStack_74 = fStack_98;
                  fStack_54 = fStack_78;
                  fStack_30 = fStack_9c;
                  fStack_2c = fStack_50;
                  sStack_d4 = CVBufTexture__AddVertices(&fStack_9c,4);
                  sStack_d2 = sStack_d4 + 1;
                  sStack_d0 = sStack_d4 + 2;
                  sStack_cc = sStack_d4 + 3;
                  sStack_ce = sStack_d0;
                  sStack_ca = sStack_d4;
                  CVBufTexture__AddIndices(&sStack_d4,6);
                }
                *(int *)(param_1 + 0x10) = *(int *)(param_1 + 0x10) + 1;
              }
              iVar7 = CCollisionSeekingRound__Helper_00491d90(&DAT_00704200);
              iVar6 = local_c8;
              iVar12 = local_b4;
              iVar11 = local_b8;
            }
          }
          local_b8 = iVar11 + 1;
        } while (local_b8 < iVar6);
        local_b4 = iVar12 + 1;
      } while (local_b4 < iVar6);
    }
    local_c4 = local_c4 + -1;
    local_b0 = (float)((int)local_b0 + 1);
  } while ((int)local_b0 < 5);
  ExceptionList = local_c;
  return;
}
