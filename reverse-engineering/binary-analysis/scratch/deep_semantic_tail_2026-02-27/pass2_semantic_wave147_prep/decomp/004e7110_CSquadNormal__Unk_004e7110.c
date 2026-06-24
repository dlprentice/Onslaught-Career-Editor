/* address: 0x004e7110 */
/* name: CSquadNormal__Unk_004e7110 */
/* signature: int __thiscall CSquadNormal__Unk_004e7110(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CSquadNormal__Unk_004e7110(void *this,void *param_1,void *param_2)

{
  float *pfVar1;
  float fVar2;
  byte bVar3;
  int iVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  int *piVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  float *pfVar12;
  uint uVar13;
  undefined4 *puVar14;
  void *this_00;
  void *unaff_EDI;
  int iVar15;
  float *pfVar16;
  bool bVar17;
  float10 fVar18;
  float10 fVar19;
  double dVar20;
  undefined4 uStack_ac;
  int iStack_a8;
  undefined4 *puStack_a4;
  float fStack_94;
  float fStack_90;
  float fStack_8c;
  undefined4 uStack_88;
  int local_84;
  undefined4 *puStack_80;
  undefined4 *puStack_7c;
  float fStack_6c;
  float afStack_60 [12];
  float afStack_30 [5];
  float fStack_1c;
  float fStack_c;

  iVar15 = 0;
  local_84 = 0;
  if ((*(int *)((int)this + 0x84) != 0) &&
     (piVar8 = (int *)(**(code **)(*(int *)this + 0x124))(), piVar8 != (int *)0x0)) {
    uVar9 = (**(code **)(*piVar8 + 0xd4))();
    *(undefined4 *)((int)this + 0x120) = uVar9;
    *(int *)((int)this + 0x7c) = piVar8[0x4e];
  }
  if ((*(int *)((int)this + 0x84) != 0) && (*(int *)((int)this + 0x120) == 1)) {
    iVar10 = (**(code **)(*(int *)this + 0x124))();
    if (iVar10 != 0) {
      iVar10 = (**(code **)(*(int *)this + 0x124))();
      *(undefined4 *)((int)this + 0x1c) = *(undefined4 *)(iVar10 + 0x1c);
      *(undefined4 *)((int)this + 0x20) = *(undefined4 *)(iVar10 + 0x20);
      *(undefined4 *)((int)this + 0x24) = *(undefined4 *)(iVar10 + 0x24);
      *(undefined4 *)((int)this + 0x28) = *(undefined4 *)(iVar10 + 0x28);
    }
    goto LAB_004e7c0f;
  }
  if (*(int *)((int)this + 0x114) == 0) goto LAB_004e7c0f;
  vector_constructor_iterator_nothrow(afStack_30,0x10,3,&LAB_00402d20);
  pfVar1 = (float *)((int)this + 0x1c);
  *(undefined4 *)((int)this + 0x110) = 0;
  *(float *)((int)this + 0x134) = *pfVar1;
  *(undefined4 *)((int)this + 0x138) = *(undefined4 *)((int)this + 0x20);
  *(undefined4 *)((int)this + 0x13c) = *(undefined4 *)((int)this + 0x24);
  *(undefined4 *)((int)this + 0x140) = *(undefined4 *)((int)this + 0x28);
  if ((*(int *)((int)this + 0xc4) == 0) || (*(int *)((int)this + 0x120) != 0)) {
    *(undefined4 *)((int)this + 0x110) = 1;
    fStack_94 = *(float *)((int)this + 0xf4);
    fStack_90 = *(float *)((int)this + 0xf8);
    fVar19 = (float10)fStack_94 - (float10)*pfVar1;
    fStack_8c = *(float *)((int)this + 0xfc);
    fVar18 = (float10)fStack_90 - (float10)*(float *)((int)this + 0x20);
    uStack_88 = *(undefined4 *)((int)this + 0x100);
    if ((float10)_DAT_005d8568 < fVar19 * fVar19 + fVar18 * fVar18) {
      fVar19 = (float10)fpatan(fVar19,fVar18);
      CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
      pfVar12 = afStack_60;
      pfVar16 = (float *)((int)this + 0x3c);
      for (iVar15 = 0xc; iVar15 != 0; iVar15 = iVar15 + -1) {
        *pfVar16 = *pfVar12;
        pfVar12 = pfVar12 + 1;
        pfVar16 = pfVar16 + 1;
      }
    }
  }
  else {
    iVar15 = CSquadNormal__Unk_004e81d0(this);
    if (iVar15 == 2) {
      iVar15 = *(int *)((int)this + 0xc4);
      fStack_94 = *pfVar1 - (*(float *)(iVar15 + 0x1c) - *pfVar1);
      fStack_90 = *(float *)((int)this + 0x20) -
                  (*(float *)(iVar15 + 0x20) - *(float *)((int)this + 0x20));
      uStack_88 = uStack_ac;
      fStack_8c = *(float *)((int)this + 0x24) -
                  (*(float *)(iVar15 + 0x24) - *(float *)((int)this + 0x24));
      *(undefined4 *)((int)this + 0x110) = 1;
      fVar2 = fStack_94 - *pfVar1;
      fVar5 = fStack_90 - *(float *)((int)this + 0x20);
      if (_DAT_005d8568 < fVar5 * fVar5 + fVar2 * fVar2) {
        vector_constructor_iterator_nothrow(afStack_60,0x10,3,&LAB_00402d20);
        fVar19 = (float10)fpatan((float10)fVar2,(float10)fVar5);
        CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
        pfVar12 = afStack_60;
        pfVar16 = (float *)((int)this + 0x3c);
        for (iVar15 = 0xc; iVar15 != 0; iVar15 = iVar15 + -1) {
          *pfVar16 = *pfVar12;
          pfVar12 = pfVar12 + 1;
          pfVar16 = pfVar16 + 1;
        }
      }
    }
    else if (iVar15 == 1) {
      iVar15 = *(int *)((int)this + 0xc4);
      fStack_94 = *(float *)(iVar15 + 0x1c);
      fStack_90 = *(float *)(iVar15 + 0x20);
      fStack_8c = *(float *)(iVar15 + 0x24);
      uStack_88 = *(undefined4 *)(iVar15 + 0x28);
      *(undefined4 *)((int)this + 0x110) = 1;
      fVar19 = (float10)*(float *)(iVar15 + 0x1c) - (float10)*pfVar1;
      fVar18 = (float10)*(float *)(iVar15 + 0x20) - (float10)*(float *)((int)this + 0x20);
      if ((float10)_DAT_005d8568 < fVar19 * fVar19 + fVar18 * fVar18) {
        fVar19 = (float10)fpatan(fVar19,fVar18);
        CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
        pfVar12 = afStack_60;
        pfVar16 = (float *)((int)this + 0x3c);
        for (iVar15 = 0xc; iVar15 != 0; iVar15 = iVar15 + -1) {
          *pfVar16 = *pfVar12;
          pfVar12 = pfVar12 + 1;
          pfVar16 = pfVar16 + 1;
        }
      }
    }
    else {
      fStack_94 = *pfVar1;
      fStack_90 = *(float *)((int)this + 0x20);
      fStack_8c = *(float *)((int)this + 0x24);
      uStack_88 = *(undefined4 *)((int)this + 0x28);
      fVar19 = (float10)*(float *)(*(int *)((int)this + 0xc4) + 0x1c) - (float10)*pfVar1;
      fVar18 = (float10)*(float *)(*(int *)((int)this + 0xc4) + 0x20) -
               (float10)*(float *)((int)this + 0x20);
      if ((float10)_DAT_005d8568 < fVar19 * fVar19 + fVar18 * fVar18) {
        fVar19 = (float10)fpatan(fVar19,fVar18);
        CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
        pfVar12 = afStack_60;
        pfVar16 = (float *)((int)this + 0x3c);
        for (iVar15 = 0xc; iVar15 != 0; iVar15 = iVar15 + -1) {
          *pfVar16 = *pfVar12;
          pfVar12 = pfVar12 + 1;
          pfVar16 = pfVar16 + 1;
        }
      }
    }
    *(float *)((int)this + 0xf4) = *pfVar1;
    *(undefined4 *)((int)this + 0xf8) = *(undefined4 *)((int)this + 0x20);
    *(undefined4 *)((int)this + 0xfc) = *(undefined4 *)((int)this + 0x24);
    *(undefined4 *)((int)this + 0x100) = *(undefined4 *)((int)this + 0x28);
  }
  fVar19 = (float10)fpatan((float10)fStack_94 - (float10)*pfVar1,
                           (float10)fStack_90 - (float10)*(float *)((int)this + 0x20));
  CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
  iVar15 = *(int *)((int)this + 0x7c);
  pfVar12 = afStack_60;
  pfVar16 = afStack_30;
  for (iVar10 = 0xc; iVar10 != 0; iVar10 = iVar10 + -1) {
    *pfVar16 = *pfVar12;
    pfVar12 = pfVar12 + 1;
    pfVar16 = pfVar16 + 1;
  }
  this_00 = DAT_008a9d7c;
  if (((iVar15 == 0) || (this_00 = DAT_008a9d80, iVar15 == 1)) && (this_00 != (void *)0x0)) {
    if (*(int *)((int)this + 0x110) == 0) {
      iVar15 = CSquadNormal__Helper_0044c720(this_00,(int)*pfVar1,*(int *)((int)this + 0x20));
      if (iVar15 != 0) {
        fStack_94 = *pfVar1;
        fStack_90 = *(float *)((int)this + 0x20);
        fStack_8c = *(float *)((int)this + 0x24);
        uStack_88 = *(undefined4 *)((int)this + 0x28);
        CSquadNormal__Helper_0044c810(this_00,(int)&fStack_94,unaff_EDI);
        *(undefined4 *)((int)this + 0x110) = 1;
      }
    }
    else {
      iVar15 = CSquadNormal__Helper_0044c720(this_00,(int)fStack_94,(int)fStack_90);
      if (iVar15 != 0) {
        CSquadNormal__Helper_0044c810(this_00,(int)&fStack_94,unaff_EDI);
      }
    }
  }
  fVar2 = fStack_90 - *(float *)((int)this + 0x20);
  if (*(int *)((int)this + 0x110) != 0) {
    fVar2 = (fStack_94 - *pfVar1) * (fStack_94 - *pfVar1) + fVar2 * fVar2;
    if ((_DAT_005d8568 < fVar2) && (*(int *)((int)this + 0xd0) != 0)) {
      fVar19 = (float10)(**(code **)(*(int *)this + 0x40))();
      dVar20 = CRT__RoundToIntegerRespectingControlWord((double)fVar19);
      puStack_a4 = (undefined4 *)(longlong)ROUND(dVar20);
      iVar15 = (int)puStack_a4 * 2;
      if (iVar15 < 2) {
        iVar15 = 2;
      }
      if (((*(int *)((int)this + 0xdc) == 0) ||
          (puStack_a4 = (undefined4 *)(longlong)ROUND(fStack_94),
          uVar11 = *(int *)((int)this + 0xd4) - (int)puStack_a4, uVar13 = (int)uVar11 >> 0x1f,
          iVar15 < (int)((uVar11 ^ uVar13) - uVar13))) ||
         (puStack_a4 = (undefined4 *)(longlong)ROUND(fStack_90),
         uVar11 = *(int *)((int)this + 0xd8) - (int)puStack_a4, uVar13 = (int)uVar11 >> 0x1f,
         iVar15 < (int)((uVar11 ^ uVar13) - uVar13))) {
        CExplosionInitThing__ClearCostGridBoundsAndBuildPath();
      }
    }
    bVar17 = _DAT_005d8568 < fVar2;
    if (*(int *)((int)this + 0xdc) == 0) {
      *(undefined4 *)((int)this + 0x108) = 0;
    }
    else {
      puStack_a4 = (undefined4 *)(longlong)ROUND(*pfVar1);
      puStack_80 = puStack_a4;
      puStack_a4 = (undefined4 *)(longlong)ROUND(*(float *)((int)this + 0x20));
      iStack_a8 = (int)puStack_a4;
      iVar15 = *(int *)((int)this + 0xe0);
      if (0 < iVar15) {
        puStack_80 = (undefined4 *)
                     ((uint)*(byte *)(*(int *)((int)this + 0xe4) + -1 + iVar15) * 2 + 1);
        iStack_a8 = (uint)*(byte *)(*(int *)((int)this + 0xec) + -1 + iVar15) * 2 + 1;
      }
      fVar2 = (float)(int)puStack_80 - *pfVar1;
      fVar5 = (float)iStack_a8 - *(float *)((int)this + 0x20);
      fVar19 = (float10)fpatan((float10)fVar2,(float10)fVar5);
      CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
      bVar17 = true;
      pfVar12 = afStack_60;
      pfVar16 = afStack_30;
      for (iVar15 = 0xc; iVar15 != 0; iVar15 = iVar15 + -1) {
        *pfVar16 = *pfVar12;
        pfVar12 = pfVar12 + 1;
        pfVar16 = pfVar16 + 1;
      }
      if (SQRT(fVar2 * fVar2 + fVar5 * fVar5) < *(float *)((int)this + 0x108) * _DAT_005d857c) {
        do {
          iVar15 = *(int *)((int)this + 0xe0) + -1;
          *(int *)((int)this + 0xe0) = iVar15;
          if (iVar15 < 1) {
            bVar17 = false;
            break;
          }
          if (0 < iVar15) {
            puStack_80 = (undefined4 *)
                         ((uint)*(byte *)(*(int *)((int)this + 0xe4) + -1 + iVar15) * 2 + 1);
            iStack_a8 = (uint)*(byte *)(*(int *)((int)this + 0xec) + -1 + iVar15) * 2 + 1;
          }
          fStack_6c = (float)iStack_a8;
          fVar2 = (float)(int)puStack_80 - *pfVar1;
          fVar5 = fStack_6c - *(float *)((int)this + 0x20);
          fVar19 = (float10)fpatan((float10)fVar2,(float10)fVar5);
          CSquadNormal__Helper_004062d0(afStack_60,(void *)(float)-fVar19,0.0,0.0,(float)unaff_EDI);
          pfVar12 = afStack_60;
          pfVar16 = afStack_30;
          for (iVar15 = 0xc; iVar15 != 0; iVar15 = iVar15 + -1) {
            *pfVar16 = *pfVar12;
            pfVar12 = pfVar12 + 1;
            pfVar16 = pfVar16 + 1;
          }
        } while (SQRT(fVar2 * fVar2 + fVar5 * fVar5) < *(float *)((int)this + 0x108) * _DAT_005d857c
                );
      }
    }
    CGenericActiveReader__SetReader((void *)((int)this + 200),(void *)0x0);
    if (bVar17) {
      iVar15 = CSquadNormal__Unk_004e7cf0((int)this);
      if (iVar15 == 0) {
        iVar15 = CSquadNormal__Unk_004e7f40((int)this);
        if (iVar15 != 0) {
          local_84 = 1;
        }
      }
      else {
        fVar2 = *(float *)((int)this + 0x108) * _DAT_005d857c;
        if (*(int *)((int)this + 0xd0) != 0) {
          Vec3__SetXYZ();
          puStack_a4 = (undefined4 *)(longlong)ROUND((float)puStack_80);
          uVar11 = (int)puStack_a4 >> 1;
          iVar15 = (int)puStack_a4 >> 4;
          puStack_a4 = (undefined4 *)(longlong)ROUND((float)puStack_7c);
          uVar11 = uVar11 & 0x80000007;
          if ((int)uVar11 < 0) {
            uVar11 = (uVar11 - 1 | 0xfffffff8) + 1;
          }
          if ((*(byte *)(((int)puStack_a4 >> 1) + iVar15 * 0x100 + *(int *)((int)this + 0xd0)) &
              (byte)(1 << ((byte)uVar11 & 0x1f))) == 0) {
            iVar15 = *(int *)((int)this + 0xe0);
            if (0 < iVar15) {
              bVar3 = *(byte *)(*(int *)((int)this + 0xec) + -1 + iVar15);
              *pfVar1 = (float)((uint)*(byte *)(*(int *)((int)this + 0xe4) + -1 + iVar15) * 2 + 1);
              *(float *)((int)this + 0x20) = (float)((uint)bVar3 * 2 + 1);
            }
          }
          else {
            *pfVar1 = afStack_30[1] * fVar2 + *pfVar1;
            *(float *)((int)this + 0x20) = fStack_1c * fVar2 + *(float *)((int)this + 0x20);
            *(float *)((int)this + 0x24) = fStack_c * fVar2 + *(float *)((int)this + 0x24);
          }
        }
      }
      if (*(int *)((int)this + 0x9c) != 1) goto LAB_004e7b72;
    }
    iVar15 = CSquadNormal__Unk_004e7cf0((int)this);
    if ((iVar15 != 0) && (_DAT_005d8568 < *(float *)((int)this + 0x104))) {
      puStack_7c = &DAT_008550a0;
      piVar8 = (int *)LinkedPtrCursor__MoveFirstAndGet(&puStack_80);
      while (piVar8 != (int *)0x0) {
        if (((piVar8 != this) && (iVar15 = (**(code **)(*piVar8 + 0x148))(), iVar15 != 0)) &&
           (fVar19 = (float10)(**(code **)(*piVar8 + 0x138))(), (float10)_DAT_005d8568 < fVar19)) {
          fVar5 = *pfVar1 - (float)piVar8[7];
          fVar6 = *(float *)((int)this + 0x20) - (float)piVar8[8];
          fVar7 = SQRT(fVar6 * fVar6 + fVar5 * fVar5);
          fVar19 = (float10)(**(code **)(*piVar8 + 0x40))();
          fVar18 = (float10)(**(code **)(*(int *)this + 0x40))();
          fVar2 = (float)((fVar18 + (float10)(float)fVar19) - (float10)fVar7);
          if ((_DAT_005d856c < fVar7) && (_DAT_005d856c < fVar2)) {
            fVar2 = fVar2 / fVar7;
            fVar5 = fVar2 * fVar5;
            fVar2 = fVar2 * fVar6;
            fStack_6c = fVar2 + *(float *)((int)this + 0x20);
            puStack_a4 = (undefined4 *)(longlong)ROUND(fVar5 + *pfVar1);
            uVar11 = (int)puStack_a4 >> 1;
            iVar15 = (int)puStack_a4 >> 4;
            puStack_a4 = (undefined4 *)(longlong)ROUND(fStack_6c);
            uVar11 = uVar11 & 0x80000007;
            if ((int)uVar11 < 0) {
              uVar11 = (uVar11 - 1 | 0xfffffff8) + 1;
            }
            if ((*(byte *)(((int)puStack_a4 >> 1) + iVar15 * 0x100 + *(int *)((int)this + 0xd0)) &
                (byte)(1 << ((byte)uVar11 & 0x1f))) != 0) {
              *pfVar1 = fVar5 + *pfVar1;
              *(float *)((int)this + 0x20) = fVar2 + *(float *)((int)this + 0x20);
              *(float *)((int)this + 0x24) = *(float *)((int)this + 0x24) + 0.0;
            }
            CGenericActiveReader__SetReader((void *)((int)this + 200),piVar8);
          }
        }
        puStack_80 = (undefined4 *)puStack_80[1];
        if (puStack_80 == (undefined4 *)0x0) {
          piVar8 = (int *)0x0;
        }
        else {
          piVar8 = (int *)*puStack_80;
        }
      }
    }
  }
LAB_004e7b72:
  iVar15 = *(int *)((int)this + 0xc4);
  bVar17 = false;
  if ((iVar15 == 0) ||
     (pfVar12 = (float *)(**(code **)(*(int *)this + 0x120))(),
     fVar2 = *(float *)(iVar15 + 0x1c) - *pfVar12, fVar5 = *(float *)(iVar15 + 0x20) - pfVar12[1],
     _DAT_005df25c <= fVar2 * fVar2 + fVar5 * fVar5)) {
    if (DAT_00672fd0 < *(float *)((int)this + 0x118)) goto LAB_004e7bc0;
    if ((*(int *)((int)this + 0x110) != 0) || (*(int *)((int)this + 0x80) != 0)) {
      CSquadNormal__Unk_004e8730(this);
    }
  }
  else {
    bVar17 = true;
LAB_004e7bc0:
    CSquadNormal__Unk_004e8930(this);
    if (bVar17) {
      *(float *)((int)this + 0x118) = DAT_00672fd0 + _DAT_005d85d4;
    }
  }
  dVar20 = CStaticShadows__Helper_0047eb80(0x6fadc8,pfVar1);
  *(float *)((int)this + 0x24) = (float)dVar20;
  CFrontEndPage__Process_NoOp(param_1,(int)unaff_EDI);
  CSquadNormal__SpawnMembers();
  CSquadNormal__Unk_004e8f80(this,(void *)0x0,(int)unaff_EDI);
  iVar15 = local_84;
LAB_004e7c0f:
  pfVar1 = (float *)((int)this + 0x124);
  iVar10 = 0;
  *pfVar1 = 0.0;
  *(undefined4 *)((int)this + 0x128) = 0;
  *(undefined4 *)((int)this + 300) = 0;
  *(undefined4 *)((int)this + 0x130) = uStack_ac;
  puVar14 = *(undefined4 **)((int)this + 0xa4);
  if (puVar14 == (undefined4 *)0x0) {
    piVar8 = (int *)0x0;
  }
  else {
    piVar8 = (int *)*puVar14;
  }
  if (piVar8 != (int *)0x0) {
    do {
      iVar4 = *piVar8;
      if (iVar4 != 0) {
        iVar10 = iVar10 + 1;
        *pfVar1 = *(float *)(iVar4 + 0x1c) + *pfVar1;
        *(float *)((int)this + 0x128) = *(float *)(iVar4 + 0x20) + *(float *)((int)this + 0x128);
        *(float *)((int)this + 300) = *(float *)(iVar4 + 0x24) + *(float *)((int)this + 300);
      }
      puVar14 = (undefined4 *)puVar14[1];
      if (puVar14 == (undefined4 *)0x0) {
        piVar8 = (int *)0x0;
      }
      else {
        piVar8 = (int *)*puVar14;
      }
    } while (piVar8 != (int *)0x0);
    if (iVar10 != 0) {
      fVar2 = (float)iVar10;
      *pfVar1 = *pfVar1 / fVar2;
      *(float *)((int)this + 0x128) = *(float *)((int)this + 0x128) / fVar2;
      *(float *)((int)this + 300) = *(float *)((int)this + 300) / fVar2;
    }
  }
  return iVar15;
}
