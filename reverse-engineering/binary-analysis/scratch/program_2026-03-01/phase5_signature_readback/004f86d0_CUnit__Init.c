/* address: 0x004f86d0 */
/* name: CUnit__Init */
/* signature: void __thiscall CUnit__Init(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnit__Init(void *this)

{
  char cVar1;
  byte bVar2;
  float fVar3;
  undefined4 uVar4;
  int *piVar5;
  void *pvVar6;
  int *piVar7;
  void *pvVar8;
  int iVar9;
  float *pfVar10;
  undefined4 *puVar11;
  undefined4 *puVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  int iVar16;
  int *unaff_ESI;
  byte *pbVar17;
  char *pcVar18;
  void *unaff_EDI;
  byte *pbVar19;
  char *pcVar20;
  bool bVar21;
  void *in_stack_00000004;
  undefined *puVar22;
  undefined4 uStack_68;
  undefined4 *puStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  float fStack_4c;
  float fStack_48;
  float fStack_44;
  undefined1 auStack_3c [48];
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d557d;
  pvStack_c = ExceptionList;
  iVar9 = *(int *)((int)in_stack_00000004 + 0x3bc);
  ExceptionList = &pvStack_c;
  *(undefined4 *)((int)in_stack_00000004 + 0x6c) = *(undefined4 *)((int)in_stack_00000004 + 0x3b4);
  *(int *)((int)this + 0x164) = iVar9;
  *(undefined4 *)((int)this + 0x224) = 0;
  if (iVar9 != 0) {
    if (*(int *)(iVar9 + 0xe0) != 7) {
      pvVar6 = (void *)OID__AllocObject(0x428,0x61,s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c,0xc0);
      local_4 = 0;
      if (pvVar6 == (void *)0x0) {
        pvVar6 = (void *)0x0;
      }
      else {
        eh_vector_constructor_iterator
                  ((void *)((int)pvVar6 + 8),0x41c,1,CResourceDescriptor__ctor,
                   CResourceDescriptor__dtor);
        *(undefined4 *)((int)pvVar6 + 0x424) = 1;
      }
      local_4 = 0xffffffff;
      if (this == (void *)0x0) {
        iVar9 = 0;
      }
      else {
        iVar9 = (int)this + 8;
      }
      *(int *)((int)pvVar6 + 0x408) = iVar9;
      *(undefined4 *)((int)pvVar6 + 4) = 1;
      pcVar18 = *(char **)(*(int *)((int)this + 0x164) + 0x2c);
      if (pcVar18 != (char *)0x0) {
        uVar14 = 0xffffffff;
        do {
          pcVar20 = pcVar18;
          if (uVar14 == 0) break;
          uVar14 = uVar14 - 1;
          pcVar20 = pcVar18 + 1;
          cVar1 = *pcVar18;
          pcVar18 = pcVar20;
        } while (cVar1 != '\0');
        uVar14 = ~uVar14;
        pcVar18 = pcVar20 + -uVar14;
        pcVar20 = (char *)((int)pvVar6 + 8);
        for (uVar15 = uVar14 >> 2; uVar15 != 0; uVar15 = uVar15 - 1) {
          *(undefined4 *)pcVar20 = *(undefined4 *)pcVar18;
          pcVar18 = pcVar18 + 4;
          pcVar20 = pcVar20 + 4;
        }
        for (uVar14 = uVar14 & 3; uVar14 != 0; uVar14 = uVar14 - 1) {
          *pcVar20 = *pcVar18;
          pcVar18 = pcVar18 + 1;
          pcVar20 = pcVar20 + 1;
        }
      }
      piVar7 = (int *)PCRTID__CreateObject(*(undefined4 *)((int)pvVar6 + 4));
      *(int **)((int)this + 0x30) = piVar7;
      if (piVar7 != (int *)0x0) {
        (**(code **)(*piVar7 + 4))((int)pvVar6 + 8);
      }
      if (pvVar6 != (void *)0x0) {
        CDXLandscape__DestroyArrayWithCallback((int)pvVar6 + 8,0x41c,1,CResourceDescriptor__dtor);
        OID__FreeObject(pvVar6);
      }
    }
    puVar11 = *(undefined4 **)(*(int *)((int)this + 0x164) + 0x3c);
    pvVar6 = in_stack_00000004;
    if (puVar11 == (undefined4 *)0x0) {
      puVar12 = (undefined4 *)0x0;
    }
    else {
      puVar12 = (undefined4 *)*puVar11;
    }
    while (puVar12 != (undefined4 *)0x0) {
      piVar7 = (int *)CWorldPhysicsManager__CreateWeaponByIndex(*puVar12,puVar12[1]);
      if (piVar7 != (int *)0x0) {
        uStack_5c = puVar12[2];
        uStack_60 = 1;
        puStack_64 = this;
        (**(code **)(*piVar7 + 0xc))(&puStack_64);
        piVar7[0x2b] = puVar12[2];
        if (((*(int **)((int)this + 0x30) != (int *)0x0) &&
            (pvVar8 = (void *)(**(code **)(**(int **)((int)this + 0x30) + 0x24))(),
            pvVar8 != (void *)0x0)) &&
           (_DAT_005d856c < *(float *)(*(int *)((int)this + 0x164) + 0xbc))) {
          switch(puVar12[2]) {
          case 1:
            puVar22 = &DAT_00633b64;
            break;
          case 2:
            puVar22 = &DAT_00633b5c;
            break;
          case 3:
            puVar22 = &DAT_00633b54;
            break;
          case 4:
            puVar22 = &DAT_00633b4c;
            break;
          case 5:
            puVar22 = &DAT_00633b44;
            break;
          case 6:
            puVar22 = &DAT_00633b3c;
            break;
          case 7:
            puVar22 = &DAT_00633b34;
            break;
          case 8:
            puVar22 = &DAT_00633b2c;
            break;
          case 9:
            puVar22 = &DAT_00633b24;
            break;
          default:
            goto switchD_004f88c2_default;
          }
          pvVar6 = (void *)CMCMech__FindSlotValueByNameAndOwner
                                     (pvVar8,(int)puVar22,(void *)0x1,(int)unaff_EDI);
switchD_004f88c2_default:
          for (; pvVar6 != (void *)0x0; pvVar6 = *(void **)((int)pvVar6 + 0x98)) {
            pbVar17 = (byte *)((int)pvVar6 + 0xdc);
            pbVar19 = &DAT_0062dd20;
            do {
              bVar2 = *pbVar17;
              bVar21 = bVar2 < *pbVar19;
              if (bVar2 != *pbVar19) {
LAB_004f895a:
                iVar9 = (1 - (uint)bVar21) - (uint)(bVar21 != 0);
                goto LAB_004f895f;
              }
              if (bVar2 == 0) break;
              bVar2 = pbVar17[1];
              bVar21 = bVar2 < pbVar19[1];
              if (bVar2 != pbVar19[1]) goto LAB_004f895a;
              pbVar17 = pbVar17 + 2;
              pbVar19 = pbVar19 + 2;
            } while (bVar2 != 0);
            iVar9 = 0;
LAB_004f895f:
            if ((iVar9 == 0) ||
               (iVar9 = CMCBuggy__StrnICmpWithLocaleLock
                                  ((void *)((int)pvVar6 + 0xdc),s_X1_Turret_00633b18,(void *)0x9),
               iVar9 == 0)) {
              piVar7[0x25] = 1;
            }
            else {
              iVar9 = _strncmp((char *)((int)pvVar6 + 0xdc),s_barrel_0062dd18,6);
              if ((iVar9 == 0) ||
                 (iVar9 = CMCBuggy__StrnICmpWithLocaleLock
                                    ((char *)((int)pvVar6 + 0xdc),s_X1_Barrel_00633b0c,(void *)0x9),
                 iVar9 == 0)) {
                *(undefined4 *)((int)this + 0x224) = 1;
                piVar7[0x26] = 1;
                pfVar10 = CExplosionInitThing__ExtractYawPitchFromMatrixIfValid
                                    (&uStack_58,pvVar6,(int)unaff_EDI);
                fVar3 = pfVar10[1];
                *(void **)((int)this + 0x220) = pvVar6;
                *(float *)((int)this + 0xf4) = fVar3;
              }
            }
          }
        }
        CSPtrSet__AddToTail((void *)((int)this + 0x17c),piVar7);
      }
      puVar11 = (undefined4 *)puVar11[1];
      if (puVar11 == (undefined4 *)0x0) {
        puVar12 = (undefined4 *)0x0;
      }
      else {
        puVar12 = (undefined4 *)*puVar11;
      }
    }
    puVar11 = *(undefined4 **)(*(int *)((int)this + 0x164) + 0x4c);
    if (puVar11 == (undefined4 *)0x0) {
      puVar12 = (undefined4 *)0x0;
    }
    else {
      puVar12 = (undefined4 *)*puVar11;
    }
    while (puVar12 != (undefined4 *)0x0) {
      pvVar6 = (void *)CWorldPhysicsManager__CreateSpawner(*puVar12,puVar12[1]);
      if (pvVar6 != (void *)0x0) {
        (*(code *)**(undefined4 **)((int)pvVar6 + 0x10))(in_stack_00000004);
        uVar14 = 0xffffffff;
        *(undefined4 *)((int)pvVar6 + 0xb4) = 0;
        *(undefined4 *)((int)pvVar6 + 0x70) = 0;
        *(undefined4 *)((int)pvVar6 + 0x5c) = 0;
        *(undefined4 *)((int)pvVar6 + 0x3bc) = 1;
        pcVar18 = &DAT_00662b2c;
        do {
          pcVar20 = pcVar18;
          if (uVar14 == 0) break;
          uVar14 = uVar14 - 1;
          pcVar20 = pcVar18 + 1;
          cVar1 = *pcVar18;
          pcVar18 = pcVar20;
        } while (cVar1 != '\0');
        uVar14 = ~uVar14;
        pcVar18 = pcVar20 + -uVar14;
        pcVar20 = (char *)((int)pvVar6 + 0xbc);
        for (uVar15 = uVar14 >> 2; uVar15 != 0; uVar15 = uVar15 - 1) {
          *(undefined4 *)pcVar20 = *(undefined4 *)pcVar18;
          pcVar18 = pcVar18 + 4;
          pcVar20 = pcVar20 + 4;
        }
        for (uVar14 = uVar14 & 3; uVar14 != 0; uVar14 = uVar14 - 1) {
          *pcVar20 = *pcVar18;
          pcVar18 = pcVar18 + 1;
          pcVar20 = pcVar20 + 1;
        }
        uVar14 = 0xffffffff;
        pcVar18 = &DAT_00662b2c;
        do {
          pcVar20 = pcVar18;
          if (uVar14 == 0) break;
          uVar14 = uVar14 - 1;
          pcVar20 = pcVar18 + 1;
          cVar1 = *pcVar18;
          pcVar18 = pcVar20;
        } while (cVar1 != '\0');
        uVar14 = ~uVar14;
        pcVar18 = pcVar20 + -uVar14;
        pcVar20 = (char *)((int)pvVar6 + 0x1bc);
        for (uVar15 = uVar14 >> 2; uVar15 != 0; uVar15 = uVar15 - 1) {
          *(undefined4 *)pcVar20 = *(undefined4 *)pcVar18;
          pcVar18 = pcVar18 + 4;
          pcVar20 = pcVar20 + 4;
        }
        for (uVar14 = uVar14 & 3; uVar14 != 0; uVar14 = uVar14 - 1) {
          *pcVar20 = *pcVar18;
          pcVar18 = pcVar18 + 1;
          pcVar20 = pcVar20 + 1;
        }
        uVar4 = puVar12[2];
        *(void **)((int)pvVar6 + 0x3d4) = this;
        *(undefined4 *)((int)pvVar6 + 1000) = uVar4;
        CSPtrSet__AddToTail((void *)((int)this + 0x18c),pvVar6);
      }
      puVar11 = (undefined4 *)puVar11[1];
      if (puVar11 == (undefined4 *)0x0) {
        puVar12 = (undefined4 *)0x0;
      }
      else {
        puVar12 = (undefined4 *)*puVar11;
      }
    }
    *(undefined4 *)((int)this + 0xf8) = *(undefined4 *)(*(int *)((int)this + 0x164) + 0xc0);
  }
  pvVar6 = in_stack_00000004;
  CActor__VFunc_09_004011e0(this,in_stack_00000004,(float)unaff_EDI);
  if (*(int *)((int)pvVar6 + 0x60) == 0) {
    puStack_64 = *(undefined4 **)((int)pvVar6 + 0x44);
    uStack_60 = *(undefined4 *)((int)pvVar6 + 0x48);
    uStack_5c = *(undefined4 *)((int)pvVar6 + 0x4c);
    *(undefined4 **)((int)this + 0x114) = puStack_64;
    *(undefined4 *)((int)this + 0x118) = uStack_60;
    *(undefined4 *)((int)this + 0x11c) = uStack_5c;
    *(undefined4 **)((int)this + 0x120) = puStack_64;
    *(undefined4 *)((int)this + 0x124) = uStack_60;
    *(undefined4 *)((int)this + 0x128) = uStack_5c;
  }
  if (*(int *)((int)this + 0x164) != 0) {
    puVar11 = *(undefined4 **)(*(int *)((int)this + 0x164) + 0x5c);
    if (puVar11 == (undefined4 *)0x0) {
      piVar7 = (int *)0x0;
    }
    else {
      piVar7 = (int *)*puVar11;
    }
    while (puStack_64 = puVar11, piVar7 != (int *)0x0) {
      pvVar8 = (void *)CWorldPhysicsManager__CreateCharacter(*piVar7);
      if (pvVar8 != (void *)0x0) {
        puVar11 = (undefined4 *)OID__AllocObject(4,0x59,s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c,0x135)
        ;
        if (puVar11 == (undefined4 *)0x0) {
          puVar11 = (undefined4 *)0x0;
        }
        else {
          *puVar11 = 0;
        }
        CGenericActiveReader__SetReader(puVar11,pvVar8);
        puVar12 = (undefined4 *)
                  OID__AllocObject(0x3c0,0x61,s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c,0x139);
        local_4 = 1;
        if (puVar12 == (undefined4 *)0x0) {
          puVar12 = (undefined4 *)0x0;
        }
        else {
          CInfluenceMap__Init();
          *puVar12 = &PTR_LAB_005dc1c0;
          puVar12[0xef] = 0;
        }
        iVar9 = 0x14;
        local_4 = 0xffffffff;
        (**(code **)(*(int *)this + 0x160))(0x14,piVar7[1],&fStack_4c,auStack_3c);
        pvVar6 = pvStack_c;
        puVar12[1] = uStack_5c;
        puVar12[2] = uStack_58;
        puVar12[3] = uStack_54;
        puVar12[4] = uStack_50;
        if (*(int *)((int)pvStack_c + 0x60) == 0) {
          puVar12[0x18] = 0;
          CExplosionInitThing__ExtractYawPitchFromMatrixIfValid(&uStack_68,&fStack_4c,iVar9);
          puVar12[0x11] = uStack_68;
          puVar12[0x12] = puStack_64;
          puVar12[0x13] = uStack_60;
        }
        puVar12[0x28] = *(undefined4 *)((int)pvVar6 + 0xa0);
        iVar9 = *piVar7;
        iVar16 = 0;
        piVar5 = (int *)*DAT_00855400;
        DAT_00855400[2] = (int)piVar5;
        if (piVar5 == (int *)0x0) {
          iVar13 = 0;
        }
        else {
          iVar13 = *piVar5;
        }
        while (iVar13 != 0) {
          if (iVar16 == iVar9) goto LAB_004f8d17;
          iVar16 = iVar16 + 1;
          piVar5 = *(int **)(DAT_00855400[2] + 4);
          DAT_00855400[2] = (int)piVar5;
          if (piVar5 == (int *)0x0) {
            iVar13 = 0;
          }
          else {
            iVar13 = *piVar5;
          }
        }
        iVar13 = 0;
LAB_004f8d17:
        puVar12[0xef] = iVar13;
        puVar12[0xeb] = *(undefined4 *)((int)pvStack_c + 0x3ac);
        uVar14 = 0xffffffff;
        puVar12[0xec] = *(undefined4 *)((int)pvStack_c + 0x3b0);
        pcVar18 = (char *)((int)pvStack_c + 0x2ac);
        do {
          pcVar20 = pcVar18;
          if (uVar14 == 0) break;
          uVar14 = uVar14 - 1;
          pcVar20 = pcVar18 + 1;
          cVar1 = *pcVar18;
          pcVar18 = pcVar20;
        } while (cVar1 != '\0');
        uVar14 = ~uVar14;
        pcVar18 = pcVar20 + -uVar14;
        pcVar20 = (char *)(puVar12 + 0xab);
        for (uVar15 = uVar14 >> 2; uVar15 != 0; uVar15 = uVar15 - 1) {
          *(undefined4 *)pcVar20 = *(undefined4 *)pcVar18;
          pcVar18 = pcVar18 + 4;
          pcVar20 = pcVar20 + 4;
        }
        for (uVar14 = uVar14 & 3; uVar14 != 0; uVar14 = uVar14 - 1) {
          *pcVar20 = *pcVar18;
          pcVar18 = pcVar18 + 1;
          pcVar20 = pcVar20 + 1;
        }
        (**(code **)(*unaff_ESI + 0x24))(puVar12);
        CUnit__SetReaderAndComputeRelativeYaw(pvVar8,(int)this,(void *)piVar7[1],(int)unaff_EDI);
        CSPtrSet__AddToTail((void *)((int)this + 0x19c),puVar11);
        OID__FreeObject(puVar12);
        puVar11 = puStack_64;
        pvVar6 = in_stack_00000004;
      }
      puVar11 = (undefined4 *)puVar11[1];
      if (puVar11 == (undefined4 *)0x0) {
        piVar7 = (int *)0x0;
      }
      else {
        piVar7 = (int *)*puVar11;
      }
    }
    pvVar8 = (void *)OID__AllocObject(8,0x10,s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c,0x15b);
    local_4 = 2;
    in_stack_00000004 = pvVar8;
    if (pvVar8 == (void *)0x0) {
      pvVar8 = (void *)0x0;
    }
    else {
      *(undefined4 *)((int)pvVar8 + 4) = 0;
      CWorldPhysicsManager__PushNodeGlobalList(unaff_EDI);
    }
    *(void **)((int)this + 0x1ac) = pvVar8;
    *(undefined4 *)((int)pvVar8 + 4) = 0;
    local_4 = 0xffffffff;
    iVar9 = 1;
    if (*(int *)(*(int *)((int)this + 0x164) + 0x18) != 0) {
      while ((((**(code **)(**(int **)((int)this + 0x30) + 0x1c))
                         (&DAT_00633b04,iVar9,&fStack_4c,auStack_3c,1,0), fStack_4c != _DAT_005d856c
              || (fStack_48 != _DAT_005d856c)) || (fStack_44 != _DAT_005d856c))) {
        pvVar8 = (void *)OID__AllocObject(8,0x10,s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c,0x164);
        local_4 = 3;
        in_stack_00000004 = pvVar8;
        if (pvVar8 == (void *)0x0) {
          pvVar8 = (void *)0x0;
        }
        else {
          *(undefined4 *)((int)pvVar8 + 4) = 0;
          CWorldPhysicsManager__PushNodeGlobalList(unaff_EDI);
        }
        local_4 = 0xffffffff;
        CSPtrSet__AddToTail((void *)((int)this + 0x1b4),pvVar8);
        iVar9 = iVar9 + 1;
      }
    }
    iVar9 = 1;
    if (*(int *)(*(int *)((int)this + 0x164) + 0x1c) != 0) {
      while ((((**(code **)(**(int **)((int)this + 0x30) + 0x1c))
                         (&DAT_00633afc,iVar9,&fStack_4c,auStack_3c,1,0), fStack_4c != _DAT_005d856c
              || (fStack_48 != _DAT_005d856c)) || (fStack_44 != _DAT_005d856c))) {
        pvVar8 = (void *)OID__AllocObject(8,0x10,s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c,0x16f);
        local_4 = 4;
        in_stack_00000004 = pvVar8;
        if (pvVar8 == (void *)0x0) {
          pvVar8 = (void *)0x0;
        }
        else {
          *(undefined4 *)((int)pvVar8 + 4) = 0;
          CWorldPhysicsManager__PushNodeGlobalList(unaff_EDI);
        }
        local_4 = 0xffffffff;
        CSPtrSet__AddToTail((void *)((int)this + 0x1c4),pvVar8);
        iVar9 = iVar9 + 1;
      }
    }
  }
  CSPtrSet__AddToHead(&DAT_008550d0,this);
  *(undefined4 *)((int)this + 0x138) = *(undefined4 *)((int)pvVar6 + 0xa0);
  for (iVar9 = 0; iVar16 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))(),
      iVar9 < *(int *)(iVar16 + 0x15c); iVar9 = iVar9 + 1) {
    iVar16 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
    pbVar19 = &DAT_0062dd20;
    pbVar17 = (byte *)(*(int *)(*(int *)(iVar16 + 0x160) + iVar9 * 4) + 0xdc);
    do {
      bVar2 = *pbVar19;
      bVar21 = bVar2 < *pbVar17;
      if (bVar2 != *pbVar17) {
LAB_004f901a:
        iVar16 = (1 - (uint)bVar21) - (uint)(bVar21 != 0);
        goto LAB_004f901f;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar19[1];
      bVar21 = bVar2 < pbVar17[1];
      if (bVar2 != pbVar17[1]) goto LAB_004f901a;
      pbVar19 = pbVar19 + 2;
      pbVar17 = pbVar17 + 2;
    } while (bVar2 != 0);
    iVar16 = 0;
LAB_004f901f:
    if (iVar16 == 0) {
      iVar16 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
      iVar16 = *(int *)(*(int *)(iVar16 + 0x160) + 8);
      *(undefined4 *)((int)this + 0x1f8) = *(undefined4 *)(iVar16 + 0x60);
      *(undefined4 *)((int)this + 0x1fc) = *(undefined4 *)(iVar16 + 100);
      *(undefined4 *)((int)this + 0x200) = *(undefined4 *)(iVar16 + 0x68);
      *(undefined4 *)((int)this + 0x204) = *(undefined4 *)(iVar16 + 0x6c);
    }
  }
  if (*(int **)((int)this + 0x148) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x148) + 0x110))(this);
  }
  if (*(int *)((int)this + 0x178) != 0) {
    CDestructableSegmentsController__Init();
  }
  if (*(int *)((int)this + 0x164) != 0) {
    CWorldMeshList__MarkUsed(*(undefined4 *)(*(int *)((int)this + 0x164) + 0xb0));
    if (*(int *)((int)this + 0x138) == 0) {
      *(int *)(&DAT_008551c0 + *(int *)(*(int *)((int)this + 0x164) + 0xe0) * 4) =
           *(int *)(&DAT_008551c0 + *(int *)(*(int *)((int)this + 0x164) + 0xe0) * 4) + 1;
    }
    else if (*(int *)((int)this + 0x138) == 1) {
      *(int *)(&DAT_00855228 + *(int *)(*(int *)((int)this + 0x164) + 0xe0) * 4) =
           *(int *)(&DAT_00855228 + *(int *)(*(int *)((int)this + 0x164) + 0xe0) * 4) + 1;
    }
  }
  CUnit__UpdateFireControlYawAndQueueEvent(this,(void *)0x0,unaff_EDI);
  *(undefined4 *)((int)this + 0x228) = 0;
  *(undefined4 *)((int)this + 0x22c) = 0;
  iVar9 = 0;
  do {
    while( true ) {
      iVar16 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
      if (*(int *)(iVar16 + 0x15c) <= iVar9) {
        *(undefined4 *)((int)this + 0x230) = 0;
        *(undefined4 *)((int)this + 0x244) = 0;
        *(undefined4 *)((int)this + 0x23c) = 0;
        *(undefined4 *)((int)this + 0x238) = 0;
        *(undefined4 *)((int)this + 0x234) = 0;
        *(undefined4 *)((int)this + 0x240) = 0;
        *(undefined4 *)((int)this + 0x248) = 0;
        if (*(int *)((int)this + 0x148) == 0) {
          if ((*(int *)((int)this + 0x138) == 1) || (*(int *)((int)this + 0x138) == 6)) {
            CSPtrSet__AddToTail(&DAT_008550c0,this);
          }
          if ((*(int *)((int)this + 0x138) == 0) || (*(int *)((int)this + 0x138) == 6)) {
            CSPtrSet__AddToTail(&DAT_008550b0,this);
          }
        }
        in_stack_00000004 = (void *)0xbf800000;
        CEventManager__AddEvent_AtTime
                  (&EVENT_MANAGER,0xfa3,this,(float *)&stack0x00000004,0,(void *)0x0,(void *)0x0);
        ExceptionList = pvStack_c;
        return;
      }
      iVar16 = (**(code **)(**(int **)((int)this + 0x30) + 0x24))();
      iVar16 = *(int *)(*(int *)(iVar16 + 0x160) + iVar9 * 4);
      if (iVar16 != 0) break;
LAB_004f9149:
      iVar9 = iVar9 + 1;
    }
    pcVar18 = (char *)(iVar16 + 0xdc);
    iVar16 = stricmp(pcVar18,s_nexus_00633af4);
    if (iVar16 != 0) {
      iVar16 = stricmp(pcVar18,s_weakpoint_00633ae8);
      if (iVar16 == 0) {
        *(undefined4 *)((int)this + 0x22c) = 1;
      }
      goto LAB_004f9149;
    }
    iVar9 = iVar9 + 1;
    *(undefined4 *)((int)this + 0x228) = 1;
  } while( true );
}
