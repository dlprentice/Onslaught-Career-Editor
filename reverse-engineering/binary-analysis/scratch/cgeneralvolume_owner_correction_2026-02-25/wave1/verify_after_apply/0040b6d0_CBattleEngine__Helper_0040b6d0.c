/* address: 0x0040b6d0 */
/* name: CBattleEngine__Helper_0040b6d0 */
/* signature: void __thiscall CBattleEngine__Helper_0040b6d0(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CBattleEngine__Helper_0040b6d0(void *this,void *param_1,void *param_2)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  undefined1 *puVar4;
  bool bVar5;
  undefined1 *puVar6;
  void *this_00;
  int iVar7;
  int *piVar8;
  float *pfVar9;
  uint uVar10;
  void *unaff_EDI;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 fVar11;
  float10 fVar12;
  double dVar13;
  int in_stack_fffffed0;
  float fStack_c8;
  undefined1 *puStack_c4;
  float fStack_c0;
  float fStack_bc;
  float fStack_b4;
  float fStack_b0;
  undefined1 *puStack_ac;
  float fStack_a8;
  float fStack_a4;
  undefined4 uStack_a0;
  float fStack_9c;
  float fStack_98;
  float fStack_94;
  float fStack_90;
  undefined4 uStack_8c;
  float fStack_88;
  float fStack_84;
  float fStack_80;
  undefined1 *puStack_78;
  void *pvStack_74;
  undefined **ppuStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  float fStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  float fStack_4c;
  float fStack_48;
  undefined4 uStack_44;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d1268;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  this_00 = (void *)(**(code **)(*(int *)this + 0x1d4))();
  pvStack_74 = this_00;
  Vec3__SetXYZ();
  fVar12 = (float10)fpatan((float10)fStack_88,(float10)fStack_84);
  fVar2 = (float)-fVar12;
  Vec3__SetXYZ();
  dVar13 = SQRT__Wrapper_004026b0(&fStack_88);
  if ((float)dVar13 <= _DAT_005d856c) {
    fStack_c0 = 0.0;
  }
  else {
    CDXTexture__Unk_0055dcb0();
    fStack_c0 = (float)extraout_ST0;
  }
  pfVar1 = (float *)((int)this + 0x1c);
  dVar13 = CEngine__Unk_005096a0
                     (this_00,(void *)*pfVar1,*(float *)((int)this + 0x20),
                      *(float *)((int)this + 0x24),*(float *)((int)this + 0x28));
  fStack_b0 = (float)dVar13;
  dVar13 = CEngine__Unk_005099a0
                     (this_00,(void *)*pfVar1,*(float *)((int)this + 0x20),
                      *(float *)((int)this + 0x24),*(float *)((int)this + 0x28));
  fStack_bc = (float)dVar13;
  CGenericActiveReader__SetReader((void *)((int)this + 0x4e0),(void *)0x0);
  if (DAT_008a9ab8 == 0) {
    *(undefined4 *)((int)this + 0x4e8) = 0;
    *(undefined4 *)((int)this + 0x4f4) = 0;
    *(undefined4 *)((int)this + 0x4ec) = 0;
    *(undefined4 *)((int)this + 0x4f8) = 0;
  }
  else {
    if (*(int *)(*(int *)((int)this_00 + 0xa4) + 0x30) != 0) {
      if (fStack_bc <= _DAT_005d856c) {
        fStack_bc = 1000.0;
      }
      iVar7 = CMapWho__GetFirstEntryWithinRadius();
      puStack_c4 = (undefined1 *)0x3e4ccccd;
      if ((*(int *)((int)this_00 + 0xa0) != 0) &&
         (*(int *)(*(int *)((int)this_00 + 0xa0) + 0xb0) != 0)) {
        puStack_c4 = (undefined1 *)0x3f4ccccd;
      }
      while (iVar7 != 0) {
        piVar8 = (int *)CMapWhoEntry__GetOwner();
        if (piVar8 != (int *)0x0) {
          if ((piVar8[0xd] & 0x10U) == 0) {
            if ((((piVar8[0xd] & 0x400000U) != 0) &&
                (iVar7 = (**(code **)(*piVar8 + 0x11c))(), iVar7 != 0)) &&
               (iVar7 = CUnit__Unk_004fd3d0(this,piVar8[0x3b],(int)unaff_EDI), iVar7 != 0)) {
              CThing__Unk_004f3ac0(piVar8,(int)&fStack_88,unaff_EDI);
              fStack_90 = fStack_80 - *(float *)((int)this + 0x24);
              fStack_94 = fStack_84 - *(float *)((int)this + 0x20);
              fStack_c8 = fStack_88 - *pfVar1;
              fVar3 = fStack_94 * fStack_94 + fStack_c8 * fStack_c8 + fStack_90 * fStack_90;
              fStack_98 = fStack_c8;
              if ((fStack_b0 * fStack_b0 <= fVar3) && (fVar3 <= fStack_bc * fStack_bc)) {
                fVar12 = (float10)fpatan((float10)fStack_c8,(float10)fStack_94);
                fVar12 = -fVar12;
                if ((_DAT_005d85c8 <= fVar2) || (fVar12 <= (float10)_DAT_005d85e4)) {
                  if ((_DAT_005d85e4 < fVar2) && (fVar12 < (float10)_DAT_005d85c8)) {
                    fVar12 = fVar12 + (float10)_DAT_005d85e0;
                  }
                }
                else {
                  fVar12 = fVar12 - (float10)_DAT_005d85e0;
                }
                dVar13 = SQRT__Wrapper_004026b0(&fStack_98);
                if ((float)dVar13 <= _DAT_005d856c) {
                  fVar11 = (float10)_DAT_005d856c;
                }
                else {
                  fStack_b4 = fStack_90 / (float)dVar13;
                  CDXTexture__Unk_0055dcb0();
                  fVar11 = extraout_ST0_01;
                }
                fStack_c8 = (float)fVar11;
                if ((_DAT_005d85c8 <= fStack_c0) || (fStack_c8 <= _DAT_005d85e4)) {
                  if ((_DAT_005d85e4 < fStack_c0) && (fStack_c8 < _DAT_005d85c8)) {
                    fVar11 = (float10)fStack_c8 + (float10)_DAT_005d85e0;
                  }
                }
                else {
                  fVar11 = (float10)fStack_c8 - (float10)_DAT_005d85e0;
                }
                puVar4 = (undefined1 *)
                         (float)(ABS((float10)(float)-((float10)fVar2 - fVar12)) +
                                ABS(-((float10)fStack_c0 - fVar11)));
                puStack_ac = puStack_c4;
                pfVar9 = (float *)(**(code **)(*piVar8 + 0x6c))();
                puVar6 = puStack_ac;
                if ((pfVar9[2] * pfVar9[2] + pfVar9[1] * pfVar9[1] + *pfVar9 * *pfVar9 <
                     _DAT_005d8c60) && ((float)_DAT_005d8604 < (float)puStack_c4)) {
                  puVar6 = _DAT_005d8604;
                }
                if ((float)puVar4 < (float)puVar6) {
                  CGenericActiveReader__SetReader((void *)((int)this + 0x4e0),piVar8);
                  puStack_c4 = puVar4;
                }
              }
            }
          }
          else {
            iVar7 = CUnit__Unk_004fd3d0(this,piVar8[0x4e],(int)unaff_EDI);
            if ((iVar7 != 0) && ((*(byte *)(piVar8 + 0xb) & 4) == 0)) {
              bVar5 = true;
              if (((piVar8[0xd] & 0x400U) != 0) &&
                 ((*(int *)((int)pvStack_74 + 0xa0) == 0 ||
                  (*(int *)(*(int *)((int)pvStack_74 + 0xa0) + 0xb0) == 0)))) {
                bVar5 = false;
              }
              iVar7 = piVar8[0x59];
              if ((((((iVar7 == 0) || (*(int *)(iVar7 + 0x124) == 0)) && (piVar8[0x85] != 0)) &&
                   ((piVar8[0x8a] == 0 && (piVar8[0x8b] == 0)))) &&
                  ((iVar7 == 0 || (*(int *)(iVar7 + 0x114) != 0)))) && (bVar5)) {
                (**(code **)(*piVar8 + 0x168))();
                fStack_a4 = fStack_38 - *(float *)((int)this + 0x24);
                fStack_a8 = fStack_3c - *(float *)((int)this + 0x20);
                puStack_ac = (undefined1 *)(fStack_40 - *pfVar1);
                fVar12 = (float10)(**(code **)(*piVar8 + 0x16c))();
                fVar3 = (float)(((float10)_DAT_005d8568 - fVar12 * (float10)_DAT_005d85fc) *
                               (float10)fStack_c0);
                iVar7 = (**(code **)(*piVar8 + 0x1a4))();
                if (iVar7 == 0) {
                  fStack_c8 = fStack_c8 * _DAT_005d85ec;
                }
                if ((fStack_b0 * fStack_b0 <= fVar3) && (fVar3 <= fStack_c8 * fStack_c8)) {
                  fVar12 = (float10)fpatan((float10)fStack_a8,(float10)fStack_a4);
                  fVar12 = -fVar12;
                  if ((_DAT_005d85c8 <= fVar2) || (fVar12 <= (float10)_DAT_005d85e4)) {
                    if ((_DAT_005d85e4 < fVar2) && (fVar12 < (float10)_DAT_005d85c8)) {
                      fVar12 = fVar12 + (float10)_DAT_005d85e0;
                    }
                  }
                  else {
                    fVar12 = fVar12 - (float10)_DAT_005d85e0;
                  }
                  fStack_b4 = (float)-((float10)fVar2 - fVar12);
                  dVar13 = SQRT__Wrapper_004026b0(&fStack_a8);
                  if ((float)dVar13 <= _DAT_005d856c) {
                    fVar12 = (float10)_DAT_005d856c;
                  }
                  else {
                    CDXTexture__Unk_0055dcb0();
                    fVar12 = extraout_ST0_00;
                  }
                  fStack_c8 = (float)fVar12;
                  if ((_DAT_005d85c8 <= fStack_c0) || (fStack_c8 <= _DAT_005d85e4)) {
                    if ((_DAT_005d85e4 < fStack_c0) && (fStack_c8 < _DAT_005d85c8)) {
                      fVar12 = (float10)fStack_c8 + (float10)_DAT_005d85e0;
                    }
                  }
                  else {
                    fVar12 = (float10)fStack_c8 - (float10)_DAT_005d85e0;
                  }
                  puVar4 = (undefined1 *)
                           (float)(ABS((float10)fStack_b4) + ABS(-((float10)fStack_c0 - fVar12)));
                  puStack_78 = puStack_c4;
                  pfVar9 = (float *)(**(code **)(*piVar8 + 0x6c))();
                  puVar6 = puStack_78;
                  if ((pfVar9[2] * pfVar9[2] + pfVar9[1] * pfVar9[1] + *pfVar9 * *pfVar9 <
                       _DAT_005d8c60) && ((float)_DAT_005d8604 < (float)puStack_c4)) {
                    puVar6 = _DAT_005d8604;
                  }
                  if ((float)puVar4 < (float)puVar6) {
                    CGenericActiveReader__SetReader((void *)((int)this + 0x4e0),piVar8);
                    puStack_c4 = puVar4;
                  }
                }
              }
            }
          }
        }
        iVar7 = CMapWho__GetNextEntryWithinRadius();
      }
    }
    if ((*(int *)((int)this + 0x4e0) != 0) &&
       ((*(uint *)(*(int *)((int)this + 0x4e0) + 0x34) & 0x100) != 0)) {
      CGenericActiveReader__SetReader((undefined4 *)((int)this + 0x4e0),(void *)0x0);
    }
    piVar8 = *(int **)((int)this + 0x4e0);
    if (piVar8 != (int *)0x0) {
      if ((*(byte *)(piVar8 + 0xd) & 0x10) == 0) {
        CThing__Unk_004f3ac0(piVar8,(int)&fStack_a8,unaff_EDI);
      }
      else {
        (**(code **)(*piVar8 + 0x168))();
      }
      fStack_5c = *pfVar1;
      uStack_58 = *(undefined4 *)((int)this + 0x20);
      uStack_54 = *(undefined4 *)((int)this + 0x24);
      uStack_50 = *(undefined4 *)((int)this + 0x28);
      fStack_4c = fStack_a8;
      uStack_6c = 0;
      uStack_68 = 0;
      uStack_64 = 0;
      fStack_48 = fStack_a4;
      uStack_44 = uStack_a0;
      fStack_40 = fStack_9c;
      ppuStack_70 = &PTR_VFuncSlot_00_00426340_005d8bfc;
      puStack_ac = &stack0xfffffed0;
      uStack_4 = 0;
      fStack_98 = 0.0;
      fStack_94 = -NAN;
      fStack_90 = 0.0;
      uStack_8c = 0xbf800000;
      CGeneralVolume__ctor_like_004098e0(&stack0xfffffed0,&ppuStack_70,in_stack_fffffed0);
      iVar7 = CWorld__Unk_0050b030();
      if ((iVar7 != 3) || (fStack_98 != *(float *)((int)this + 0x4e0))) {
        CGenericActiveReader__SetReader((void *)((int)this + 0x4e0),(void *)0x0);
      }
      uStack_4 = 0xffffffff;
    }
    uVar10 = Random__NextLCGAbs(DAT_008a9d9c);
    puStack_ac = (undefined1 *)(uVar10 & 0x8000ffff);
    if ((int)puStack_ac < 0) {
      puStack_ac = (undefined1 *)(((int)puStack_ac - 1U | 0xffff0000) + 1);
    }
    fStack_b4 = (float)(int)puStack_ac * _DAT_005d8c5c + DAT_00672fd0 + (float)_DAT_005d8604;
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0x1773,this,&fStack_b4,0,(void *)0x0,param_1);
  }
  ExceptionList = pvStack_c;
  return;
}
