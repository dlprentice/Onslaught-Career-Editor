/* address: 0x004aa940 */
/* name: CMesh__Unk_004aa940 */
/* signature: int __thiscall CMesh__Unk_004aa940(void * this, int param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CMesh__Unk_004aa940(void *this,int param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  void *pvVar3;
  float *pfVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  void *unaff_EDI;
  float local_4b8;
  int local_4b4;
  float local_4b0 [150];
  void *local_258 [150];

  iVar7 = 0;
  local_4b4 = 0;
  iVar8 = *(int *)((int)this + 0x15c);
  if (iVar8 == 0) {
    CConsole__Printf(&DAT_0066f580,s_WARNING__trying_to_get_random_ve_0062fce0);
    *(undefined4 *)param_1 = 0;
    *(undefined4 *)(param_1 + 4) = 0;
    *(undefined4 *)(param_1 + 8) = 0;
    return param_1;
  }
  if (0xf < iVar8) {
    iVar6 = 0;
    local_4b8 = 0.0;
    if (0 < iVar8) {
      do {
        iVar8 = *(int *)(*(int *)((int)this + 0x160) + iVar6 * 4);
        *(int *)param_2 = iVar8;
        iVar8 = CMesh__Helper_004b0cd0(iVar8);
        if ((iVar8 != 0) &&
           (iVar8 = CMesh__Helper_004b0cd0(*(int *)param_2), *(int *)(iVar8 + 0x8c) == 1)) {
          iVar8 = *(int *)((int)*(void **)param_2 + 0xfc);
          if (iVar8 != 0) {
            if (iVar7 < 0x96) {
              fVar1 = *(float *)(iVar8 + 0x24);
              local_258[iVar7] = *(void **)param_2;
              local_4b0[iVar7] = fVar1;
              local_4b8 = fVar1 + local_4b8;
              iVar7 = iVar7 + 1;
            }
            else {
              CConsole__Printf(&DAT_0066f580,s_WARNING__Not_enough_mp_allocated_0062fcac);
            }
          }
        }
        iVar6 = iVar6 + 1;
      } while (iVar6 < *(int *)((int)this + 0x15c));
    }
    if (0 < iVar7) {
      pfVar4 = local_4b0;
      iVar8 = iVar7;
      do {
        iVar8 = iVar8 + -1;
        *pfVar4 = *pfVar4 / local_4b8;
        pfVar4 = pfVar4 + 1;
      } while (iVar8 != 0);
    }
    do {
      uVar5 = Random__NextLCGAbs(DAT_008a9d9c);
      uVar5 = uVar5 & 0x8000ffff;
      if ((int)uVar5 < 0) {
        uVar5 = (uVar5 - 1 | 0xffff0000) + 1;
      }
      iVar8 = 0;
      fVar1 = (float)(int)uVar5 * _DAT_005d8d54;
      if (0 < iVar7) {
        do {
          iVar6 = Random__NextLCGAbs(DAT_008a9d9c);
          fVar2 = local_4b0[iVar6 % iVar7];
          pvVar3 = local_258[iVar6 % iVar7];
          *(void **)param_2 = pvVar3;
          if (fVar1 <= fVar2) {
            CMesh__Helper_004b25d0(pvVar3,param_1,unaff_EDI);
            return param_1;
          }
          iVar8 = iVar8 + 1;
        } while (iVar8 < iVar7);
      }
      local_4b4 = local_4b4 + 1;
    } while (local_4b4 < 100);
    if (iVar7 < 1) {
      CConsole__Printf(&DAT_0066f580,s_WARNING__trying_to_get_random_ve_0062fce0);
      *(undefined4 *)param_1 = 0;
      *(undefined4 *)(param_1 + 4) = 0;
      *(undefined4 *)(param_1 + 8) = 0;
      return param_1;
    }
    CMesh__Helper_004b25d0(local_258[0],param_1,unaff_EDI);
    return param_1;
  }
  iVar8 = 0xf;
  do {
    iVar7 = Random__NextLCGAbs(DAT_008a9d9c);
    iVar7 = *(int *)(*(int *)((int)this + 0x160) + (iVar7 % *(int *)((int)this + 0x15c)) * 4);
    *(int *)param_2 = iVar7;
    pvVar3 = (void *)CMesh__Helper_004b0cd0(iVar7);
    iVar8 = iVar8 + -1;
    if ((pvVar3 != (void *)0x0) && (*(int *)((int)pvVar3 + 0x8c) == 1)) break;
  } while (0 < iVar8);
  if (iVar8 != 0) {
    CMesh__Helper_004b25d0(pvVar3,param_1,unaff_EDI);
    return param_1;
  }
  *(undefined4 *)param_1 = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  return param_1;
}
