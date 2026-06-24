/* address: 0x005718c0 */
/* name: CFastVB__MergeAndOrderStripBatches */
/* signature: void __thiscall CFastVB__MergeAndOrderStripBatches(void * this, void * param_1, int param_2, int param_3, int param_4, int param_5) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__MergeAndOrderStripBatches
          (void *this,void *param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  uint *puVar2;
  float fVar3;
  uint uVar4;
  uint uVar5;
  bool bVar6;
  bool bVar7;
  char cVar8;
  byte bVar9;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  undefined4 extraout_EAX_02;
  int *extraout_EAX_03;
  int extraout_EAX_04;
  undefined3 extraout_var;
  uint uVar10;
  uint uVar11;
  int *piVar12;
  undefined4 *puVar13;
  int iVar14;
  uint uVar15;
  void *unaff_EDI;
  uint uVar16;
  int iVar17;
  void *pvVar18;
  uint uVar19;
  double dVar20;
  bool local_82;
  undefined1 local_81;
  undefined4 *local_80;
  int local_7c;
  int local_78;
  int local_74;
  float local_70;
  void *local_6c;
  uint local_68;
  int *local_64;
  int local_60;
  int local_5c;
  int *local_58;
  undefined4 local_54;
  uint local_50;
  uint local_4c;
  undefined4 *local_48;
  uint local_44;
  uint local_40;
  uint local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined1 local_2c [4];
  void *local_28;
  int local_24;
  undefined4 local_20;
  undefined1 local_1c [4];
  void *local_18;
  int local_14;
  undefined4 local_10;
  void *local_c;
  undefined1 *puStack_8;
  int local_4;

  puStack_8 = &LAB_005d7f66;
  local_c = ExceptionList;
  piVar12 = *(int **)((int)this + 0x10);
  local_18 = (void *)0x0;
  local_14 = 0;
  local_10 = 0;
  local_4 = 0;
  local_7c = 0;
  ExceptionList = &local_c;
  local_6c = this;
  local_64 = piVar12;
  for (local_4c = 0;
      (iVar17 = *(int *)((int)param_1 + 4), iVar17 != 0 &&
      (local_4c < (uint)(*(int *)((int)param_1 + 8) - iVar17 >> 2))); local_4c = local_4c + 1) {
    local_3c = local_3c & 0xffffff00;
    local_68 = 0;
    uVar16 = 0;
    while( true ) {
      iVar14 = *(int *)(*(int *)(iVar17 + local_7c) + 0x10);
      if ((iVar14 == 0) ||
         ((uint)(*(int *)(*(int *)(iVar17 + local_7c) + 0x14) - iVar14 >> 2) <= uVar16)) break;
      bVar6 = CFastVB__HasDuplicateTriangleIndices32
                        (*(void **)(*(int *)(*(int *)(iVar17 + local_7c) + 0x10) + uVar16 * 4));
      if (!bVar6) {
        local_68 = local_68 + 1;
      }
      uVar16 = uVar16 + 1;
      piVar12 = local_64;
    }
    if ((int)piVar12 < (int)local_68) {
      local_50 = (int)local_68 / (int)piVar12;
      local_70 = (float)((int)local_68 % (int)piVar12);
      local_74 = 0;
      local_68 = 0;
      if (0 < (int)local_50) {
        local_5c = 0;
        local_58 = piVar12;
        do {
          CFastVB__Helper_00426fd0(0x2c);
          local_4._0_1_ = 1;
          local_48 = extraout_EAX;
          if (extraout_EAX == (undefined4 *)0x0) {
            puVar13 = (undefined4 *)0x0;
          }
          else {
            *extraout_EAX = 0;
            extraout_EAX[1] = 0;
            extraout_EAX[2] = local_3c;
            CTexture__Helper_00572f00(extraout_EAX + 3,&local_81,unaff_EDI);
            extraout_EAX[7] = 0;
            extraout_EAX[8] = 0xffffffff;
            *(undefined1 *)(extraout_EAX + 9) = 0;
            extraout_EAX[10] = 0;
            puVar13 = extraout_EAX;
          }
          iVar17 = local_5c + local_74;
          local_4 = (uint)local_4._1_3_ << 8;
          bVar6 = true;
          local_80 = puVar13;
          if (iVar17 < local_74 + (int)local_58) {
            local_78 = iVar17 + 1;
            iVar14 = iVar17 * 4;
            local_60 = local_74 + (int)local_58;
            do {
              local_48 = *(undefined4 **)(*(int *)(*(int *)((int)param_1 + 4) + local_7c) + 0x10);
              bVar7 = CFastVB__HasDuplicateTriangleIndices32(*(void **)(iVar14 + (int)local_48));
              if (bVar7) {
                local_74 = local_74 + 1;
                local_60 = local_60 + 1;
                if (((local_78 == local_60) &&
                    (((local_68 != local_50 - 1 || (3 < (int)local_70)) || ((int)local_70 < 1)))) ||
                   (bVar6)) {
                  local_78 = local_78 + 1;
                }
                else {
                  local_78 = local_78 + 1;
                  CFastVB__InsertDwordAndGrow
                            (puVar13 + 3,puVar13[5],(void *)(iVar14 + (int)local_48),unaff_EDI);
                  puVar13 = local_80;
                }
              }
              else {
                local_78 = local_78 + 1;
                CFastVB__InsertDwordAndGrow
                          (puVar13 + 3,puVar13[5],(void *)(iVar14 + (int)local_48),unaff_EDI);
                bVar6 = false;
                puVar13 = local_80;
              }
              iVar17 = iVar17 + 1;
              iVar14 = iVar14 + 4;
              piVar12 = local_64;
            } while (iVar17 < local_60);
          }
          if (((local_68 == local_50 - 1) && ((int)local_70 < 4)) && (0 < (int)local_70)) {
            local_60 = 0;
            iVar17 = iVar17 * 4;
            do {
              iVar14 = *(int *)(*(int *)(*(int *)((int)param_1 + 4) + local_7c) + 0x10);
              bVar6 = CFastVB__HasDuplicateTriangleIndices32(*(void **)(iVar17 + iVar14));
              if (bVar6) {
                CFastVB__InsertDwordAndGrow
                          (puVar13 + 3,puVar13[5],(void *)(iVar17 + iVar14),unaff_EDI);
                local_74 = local_74 + 1;
              }
              else {
                CFastVB__InsertDwordAndGrow
                          (puVar13 + 3,puVar13[5],(void *)(iVar17 + iVar14),unaff_EDI);
                local_60 = local_60 + 1;
              }
              iVar17 = iVar17 + 4;
              puVar13 = local_80;
            } while (local_60 < (int)local_70);
            local_70 = 0.0;
            piVar12 = local_64;
          }
          CFastVB__InsertDwordAndGrow(local_1c,local_14,&local_80,unaff_EDI);
          local_68 = local_68 + 1;
          local_5c = local_5c + (int)piVar12;
          local_58 = (int *)((int)local_58 + (int)piVar12);
        } while ((int)local_68 < (int)local_50);
      }
      fVar3 = local_70;
      iVar17 = 0;
      iVar14 = local_68 * (int)piVar12 + local_74;
      if (local_70 != 0.0) {
        CFastVB__Helper_00426fd0(0x2c);
        if (extraout_EAX_00 == (undefined4 *)0x0) {
          local_80 = (undefined4 *)0x0;
        }
        else {
          *extraout_EAX_00 = 0;
          extraout_EAX_00[1] = 0;
          extraout_EAX_00[2] = local_3c;
          *(undefined1 *)(extraout_EAX_00 + 3) = local_81;
          extraout_EAX_00[4] = 0;
          extraout_EAX_00[5] = 0;
          extraout_EAX_00[6] = 0;
          extraout_EAX_00[7] = 0;
          extraout_EAX_00[8] = 0xffffffff;
          *(undefined1 *)(extraout_EAX_00 + 9) = 0;
          extraout_EAX_00[10] = 0;
          local_80 = extraout_EAX_00;
        }
        bVar6 = true;
        if (0 < (int)fVar3) {
          iVar14 = iVar14 * 4;
          do {
            iVar1 = *(int *)(*(int *)(*(int *)((int)param_1 + 4) + local_7c) + 0x10);
            bVar7 = CFastVB__HasDuplicateTriangleIndices32(*(void **)(iVar1 + iVar14));
            if (bVar7) {
              if (!bVar6) {
                CFastVB__InsertDwordSpanFilled
                          (local_80 + 3,local_80[5],(void *)0x1,iVar1 + iVar14,unaff_EDI);
              }
            }
            else {
              iVar17 = iVar17 + 1;
              CFastVB__InsertDwordSpanFilled
                        (local_80 + 3,local_80[5],(void *)0x1,iVar1 + iVar14,unaff_EDI);
              bVar6 = false;
            }
            iVar14 = iVar14 + 4;
            piVar12 = local_64;
          } while (iVar17 < (int)local_70);
        }
        goto LAB_00571cd8;
      }
    }
    else {
      CFastVB__Helper_00426fd0(0x2c);
      iVar17 = local_7c;
      if (extraout_EAX_01 == (undefined4 *)0x0) {
        local_80 = (undefined4 *)0x0;
      }
      else {
        *extraout_EAX_01 = 0;
        extraout_EAX_01[1] = 0;
        extraout_EAX_01[2] = local_3c;
        *(undefined1 *)(extraout_EAX_01 + 3) = local_81;
        extraout_EAX_01[4] = 0;
        extraout_EAX_01[5] = 0;
        extraout_EAX_01[6] = 0;
        extraout_EAX_01[7] = 0;
        extraout_EAX_01[8] = 0xffffffff;
        *(undefined1 *)(extraout_EAX_01 + 9) = 0;
        extraout_EAX_01[10] = 0;
        local_80 = extraout_EAX_01;
      }
      uVar16 = 0;
      while( true ) {
        iVar14 = *(int *)(iVar17 + *(int *)((int)param_1 + 4));
        if ((*(int *)(iVar14 + 0x10) == 0) ||
           ((uint)(*(int *)(iVar14 + 0x14) - *(int *)(iVar14 + 0x10) >> 2) <= uVar16)) break;
        CFastVB__InsertDwordSpanFilled
                  (local_80 + 3,local_80[5],(void *)0x1,*(int *)(iVar14 + 0x10) + uVar16 * 4,
                   unaff_EDI);
        uVar16 = uVar16 + 1;
      }
LAB_00571cd8:
      CFastVB__InsertDwordSpanFilled(local_1c,local_14,(void *)0x1,(uint)&local_80,unaff_EDI);
    }
    local_7c = local_7c + 4;
  }
  local_28 = (void *)0x0;
  local_2c[0] = local_81;
  local_24 = 0;
  local_20 = 0;
  local_4._0_1_ = 2;
  CTexture__Helper_00570dd0(local_6c,(int)local_1c,(int)local_2c,param_4,(int)unaff_EDI);
  CFastVB__CopyDwordRange_Strict
            (*(void **)(param_2 + 8),*(void **)(param_2 + 8),*(void **)(param_2 + 4));
  VFuncSlot_12_00405db0();
  *(undefined4 *)(param_2 + 8) = extraout_EAX_02;
  if ((local_28 != (void *)0x0) &&
     (local_48 = (undefined4 *)(local_24 - (int)local_28 >> 2), local_48 != (undefined4 *)0x0)) {
    CFastVB__Helper_00426fd0(8);
    local_4._0_1_ = 3;
    if (extraout_EAX_03 == (int *)0x0) {
      local_64 = (int *)0x0;
    }
    else {
      iVar17 = *(int *)((int)local_6c + 0x10);
      extraout_EAX_03[1] = iVar17;
      CFastVB__Helper_00426fd0(iVar17 << 2);
      *extraout_EAX_03 = extraout_EAX_04;
      iVar17 = 0;
      local_64 = extraout_EAX_03;
      if (0 < extraout_EAX_03[1]) {
        do {
          iVar17 = iVar17 + 1;
          *(undefined4 *)(*extraout_EAX_03 + -4 + iVar17 * 4) = 0xffffffff;
        } while (iVar17 < extraout_EAX_03[1]);
      }
    }
    local_4._0_1_ = 2;
    local_50 = 0;
    local_48 = (undefined4 *)0x461c4000;
    uVar16 = 0;
    pvVar18 = local_28;
    while ((uVar15 = uVar16, uVar16 = local_50, piVar12 = local_64, pvVar18 != (void *)0x0 &&
           (uVar15 < (uint)(local_24 - (int)pvVar18 >> 2)))) {
      uVar11 = 0;
      uVar16 = 0;
      local_4c = 0;
      while( true ) {
        iVar17 = *(int *)((int)pvVar18 + uVar15 * 4);
        iVar14 = *(int *)(iVar17 + 0x10);
        if ((iVar14 == 0) || ((uint)(*(int *)(iVar17 + 0x14) - iVar14 >> 2) <= uVar16)) break;
        cVar8 = CFastVB__CountResolvedOppositeEdges(*(void **)(iVar14 + uVar16 * 4),param_3);
        uVar11 = uVar11 + CONCAT31(extraout_var,cVar8);
        uVar16 = uVar16 + 1;
        pvVar18 = local_28;
      }
      iVar17 = *(int *)((int)pvVar18 + uVar15 * 4);
      iVar14 = *(int *)(iVar17 + 0x10);
      if (iVar14 == 0) {
        local_58 = (int *)0x0;
      }
      else {
        local_58 = (int *)(*(int *)(iVar17 + 0x14) - iVar14 >> 2);
      }
      local_54 = 0;
      local_4c = uVar11;
      if ((float)local_48 <= (float)(int)uVar11 / (float)(int)local_58) {
        uVar16 = uVar15 + 1;
      }
      else {
        uVar16 = uVar15 + 1;
        local_50 = uVar15;
        local_48 = (undefined4 *)((float)(int)uVar11 / (float)(int)local_58);
      }
    }
    CFastVB__SeedVertexCacheFromTriangleRefs(local_64,*(int *)((int)pvVar18 + local_50 * 4));
    CFastVB__InsertDwordSpanFilled
              ((void *)param_2,*(int *)(param_2 + 8),(void *)0x1,(uint)((int)local_28 + uVar16 * 4),
               unaff_EDI);
    *(undefined1 *)(*(int *)((int)local_28 + uVar16 * 4) + 0x24) = 1;
    iVar17 = *(int *)((int)local_28 + uVar16 * 4);
    iVar14 = *(int *)(iVar17 + 0x10);
    if (iVar14 == 0) {
      bVar9 = 0;
    }
    else {
      bVar9 = (byte)(*(int *)(iVar17 + 0x14) - iVar14 >> 2);
    }
    local_82 = (bool)(~bVar9 & 1);
LAB_00571fa8:
    local_70 = -1.0;
    uVar16 = 0;
    while ((uVar15 = uVar16, uVar16 = local_4c, local_68 = uVar15, local_28 != (void *)0x0 &&
           (uVar15 < (uint)(local_24 - (int)local_28 >> 2)))) {
      iVar17 = *(int *)((int)local_28 + uVar15 * 4);
      if (*(char *)(iVar17 + 0x24) == '\0') {
        dVar20 = CTexture__Helper_005723c0(piVar12,iVar17);
        fVar3 = (float)dVar20;
        if (fVar3 <= local_70) {
          if (local_70 <= fVar3) {
            iVar17 = *(int *)((int)local_28 + uVar15 * 4);
            if (*(int *)(iVar17 + 0x10) == 0) {
              iVar14 = 0;
            }
            else {
              iVar14 = *(int *)(iVar17 + 0x14) - *(int *)(iVar17 + 0x10) >> 2;
            }
            local_48 = *(undefined4 **)(iVar17 + 0x10);
            puVar2 = (uint *)*local_48;
            local_38 = 0xffffffff;
            uVar16 = *puVar2;
            uVar15 = puVar2[1];
            local_3c = puVar2[2];
            local_34 = 0xffffffff;
            local_30 = 0xffffffff;
            uVar11 = uVar15;
            local_44 = uVar16;
            local_40 = uVar15;
            if (1 < iVar14) {
              uVar10 = CFastVB__AreTriangleVertexSetsEquivalent((void *)local_48[1],&local_44);
              uVar19 = uVar16;
              uVar4 = uVar16;
              uVar5 = local_3c;
              if ((uVar10 == uVar15) ||
                 (uVar11 = local_3c, uVar19 = uVar15, uVar4 = local_40, uVar5 = uVar16,
                 uVar10 == local_3c)) {
                local_3c = uVar5;
                local_40 = uVar4;
                uVar16 = uVar11;
                uVar15 = uVar19;
                local_44 = uVar11;
              }
              uVar11 = uVar15;
              if (((2 < iVar14) &&
                  (CFastVB__GetSharedVerticesBetweenTriangles
                             ((void *)local_48[2],&local_44,&local_50,&local_58), local_50 == uVar15
                  )) && (local_58 == (int *)0xffffffff)) {
                uVar11 = local_3c;
                local_3c = uVar15;
              }
            }
            bVar6 = CFastVB__IsDirectedEdgeInTriangle(puVar2,uVar16,uVar11);
            piVar12 = local_64;
            uVar15 = local_68;
            if (local_82 == bVar6) {
              local_4c = local_68;
            }
          }
          goto LAB_00572101;
        }
        uVar16 = uVar15 + 1;
        local_70 = fVar3;
        local_4c = uVar15;
      }
      else {
LAB_00572101:
        uVar16 = uVar15 + 1;
      }
    }
    if (local_70 != _DAT_005e6a38) {
      *(undefined1 *)(*(int *)((int)local_28 + local_4c * 4) + 0x24) = 1;
      CFastVB__SeedVertexCacheFromTriangleRefs(piVar12,*(int *)((int)local_28 + local_4c * 4));
      CFastVB__InsertDwordSpanFilled
                ((void *)param_2,*(int *)(param_2 + 8),(void *)0x1,
                 (uint)((int)local_28 + uVar16 * 4),unaff_EDI);
      iVar17 = *(int *)((int)local_28 + uVar16 * 4);
      iVar14 = *(int *)(iVar17 + 0x10);
      if (iVar14 == 0) {
        uVar16 = 0;
      }
      else {
        uVar16 = *(int *)(iVar17 + 0x14) - iVar14 >> 2;
      }
      if ((uVar16 & 1) != 0) {
        local_82 = local_82 == false;
      }
      goto LAB_00571fa8;
    }
    if (piVar12 != (int *)0x0) {
      OID__FreeObject_Callback((void *)*piVar12);
      *piVar12 = 0;
      OID__FreeObject_Callback(piVar12);
    }
  }
  OID__FreeObject_Callback(local_28);
  local_28 = (void *)0x0;
  local_24 = 0;
  local_20 = 0;
  OID__FreeObject_Callback(local_18);
  ExceptionList = local_c;
  return;
}
