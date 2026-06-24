/* address: 0x004b82b0 */
/* name: CUnitAI__Unk_004b82b0 */
/* signature: void __thiscall CUnitAI__Unk_004b82b0(void * this, int param_1, float param_2, float param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CUnitAI__Unk_004b82b0(void *this,int param_1,float param_2,float param_3,int param_4)

{
  int *seed;
  int iVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  bool bVar9;
  double dVar10;
  float local_24;
  float local_20;
  uint local_1c;
  float local_18;
  float local_14;
  int local_c;

  if (*(int *)((int)this + 8) == 0) {
    return;
  }
  iVar1 = *(int *)((int)this + 0x28);
  seed = (int *)((int)this + 0x28);
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  local_24 = *(float *)((int)this + 0x20);
  iVar6 = Random__NextLCGAbs(seed);
  if (((float)(iVar6 % 200) * _DAT_005d85fc < *(float *)((int)this + 0x20)) &&
     (local_24 = *(float *)((int)this + 0x20) + _DAT_005d8604, local_24 < _DAT_005d8568)) {
    local_24 = 1.0;
  }
  bVar9 = *(float *)((int)this + 0x1b4) + _DAT_005d8578 < DAT_00672fd0;
  if (*(int *)((int)this + 0x1a8) == 5) {
    if (bVar9) {
      *(float *)((int)this + 0x1b4) = DAT_00672fd0;
      uVar7 = Random__NextLCGAbs(seed);
      uVar7 = uVar7 & 0x80000001;
      bVar9 = uVar7 == 0;
      if ((int)uVar7 < 0) {
        bVar9 = (uVar7 - 1 | 0xfffffffe) == 0xffffffff;
      }
      if (bVar9) {
        iVar6 = Random__NextLCGAbs(seed);
        if (iVar6 % 7 == 0) {
          iVar6 = Random__NextLCGAbs(seed);
          *(int *)((int)this + 0x1ac) = iVar6 % 5;
        }
        uVar7 = *(uint *)((int)this + 0x1ac);
        uVar8 = uVar7 & 0x80000001;
        bVar9 = uVar8 == 0;
        if ((int)uVar8 < 0) {
          bVar9 = (uVar8 - 1 | 0xfffffffe) == 0xffffffff;
        }
        if (bVar9) {
          iVar6 = uVar7 + 1;
        }
        else {
          iVar6 = uVar7 - 1;
        }
        *(int *)((int)this + 0x1ac) = iVar6;
        *(undefined4 *)((int)this + 0x1b0) =
             *(undefined4 *)((int)this + (iVar6 + *(int *)((int)this + 0x1a8) * 6) * 4 + 0x34);
      }
    }
  }
  else if (bVar9) {
    *(float *)((int)this + 0x1b4) = DAT_00672fd0;
    uVar7 = Random__NextLCGAbs(seed);
    uVar7 = uVar7 & 0x80000001;
    bVar9 = uVar7 == 0;
    if ((int)uVar7 < 0) {
      bVar9 = (uVar7 - 1 | 0xfffffffe) == 0xffffffff;
    }
    if (bVar9) {
      iVar6 = *(int *)((int)this + 0x1ac);
      do {
        uVar7 = Random__NextLCGAbs(seed);
        dVar10 = (double)(uVar7 & 0xff) * _DAT_005dc700;
        if ((double)_DAT_005d8c44 <= dVar10) {
          if ((double)_DAT_005d857c <= dVar10) {
            if ((double)_DAT_005db538 <= dVar10) {
              *(undefined4 *)((int)this + 0x1ac) = 3;
            }
            else {
              *(undefined4 *)((int)this + 0x1ac) = 2;
            }
          }
          else {
            *(undefined4 *)((int)this + 0x1ac) = 1;
          }
        }
        else {
          *(undefined4 *)((int)this + 0x1ac) = 0;
        }
      } while (iVar6 == *(int *)((int)this + 0x1ac));
      *(undefined4 *)((int)this + 0x1b0) =
           *(undefined4 *)
            ((int)this + (*(int *)((int)this + 0x1ac) + *(int *)((int)this + 0x1a8) * 6) * 4 + 0x34)
      ;
    }
  }
  if (*(int *)((int)this + 0x24) == 0) {
    uVar7 = 0x40;
    if (_DAT_005d8cb4 < local_24) {
      uVar7 = Random__NextLCGAbs(seed);
      uVar7 = uVar7 & 0x8000003f;
      if ((int)uVar7 < 0) {
        uVar7 = (uVar7 - 1 | 0xffffffc0) + 1;
      }
    }
    local_18 = 0.0;
    if (_DAT_005d85c0 < local_24) {
      iVar6 = Random__NextLCGAbs(seed);
      local_18 = (float)(iVar6 % 100) * _DAT_005d8c98 * local_24;
    }
    fVar5 = local_18;
    fVar2 = local_18 + _DAT_005d8568;
    local_20 = 0.0;
    if (_DAT_005d85c0 < local_24) {
      iVar6 = Random__NextLCGAbs(seed);
      local_20 = (float)(iVar6 % 100) * _DAT_005dc6f8 * local_24;
    }
    fVar3 = local_20 + _DAT_005d8568;
    local_1c = 5;
    do {
      local_14 = local_20;
      local_18 = fVar3;
      if ((float)_DAT_005dc6f0 < local_24) {
        fVar4 = local_24;
        if (local_24 < _DAT_005d85ec) {
          fVar4 = _DAT_005d85ec;
        }
        uVar8 = local_1c & 0x80000001;
        bVar9 = uVar8 == 0;
        if ((int)uVar8 < 0) {
          bVar9 = (uVar8 - 1 | 0xfffffffe) == 0xffffffff;
        }
        fVar4 = fVar4 * (float)(int)local_1c * _DAT_005dc6e8;
        if (bVar9) {
          local_14 = fVar4 + local_20;
          local_18 = local_14 + _DAT_005d8568;
        }
        else {
          local_14 = local_20 - fVar4;
          local_18 = (_DAT_005d8568 - fVar4) + local_20;
        }
      }
      if (*(void **)((int)this + 0x1b0) != (void *)0x0) {
        CVBufTexture__DrawSpriteEx
                  ((float)param_1 + _DAT_005d8bc0,param_2 - _DAT_005d8bc0,
                   (float)(int)param_3 * _DAT_005dc6e4,*(void **)((int)this + 0x1b0),2,0,1.0,0.0,
                   (float)(uVar7 * 0x1000000 + 0xffffff),0.75,0.75,local_14,local_18,fVar5,fVar2);
      }
      local_1c = local_1c - 1;
    } while (-1 < (int)local_1c);
  }
  iVar6 = Random__NextLCGAbs(seed);
  fVar2 = (float)(iVar6 % 100) * _DAT_005d85fc;
  iVar6 = Random__NextLCGAbs(seed);
  fVar5 = (float)(iVar6 % 100) * _DAT_005d85fc;
  iVar6 = Random__NextLCGAbs(seed);
  local_c = (int)(longlong)ROUND((local_24 + _DAT_005d8bd8) * (float)(iVar6 % 10 + 0x28));
  CVBufTexture__DrawSpriteEx
            ((float)param_1,param_2,(float)(int)param_3 * _DAT_005dc6e4,
             *(void **)((int)this + 0x1a4),2,0,1.0,0.0,(float)(local_c * 0x1000000 + 0xffffff),1.0,
             1.0,fVar2,fVar2 + _DAT_005d8568,fVar5,fVar5 + _DAT_005d8568);
  fVar2 = *(float *)(*(int *)((int)this + 8) + 0x20);
  if ((*(int *)((int)this + 0x24) == 0) && (fVar2 < local_24)) {
    if (DAT_008a9ac4 != 0) goto LAB_004b87eb;
    dVar10 = PtrFloatAt4__GetOrOne(&DAT_0088a0a8);
    fVar5 = *(float *)((int)this + 0x20) - (_DAT_005db538 / (float)dVar10) * _DAT_005dc6e0;
    *(float *)((int)this + 0x20) = fVar5;
    if (fVar5 < fVar2) {
      *(float *)((int)this + 0x20) = fVar2;
    }
  }
  if (DAT_008a9ac4 == 0) {
    return;
  }
LAB_004b87eb:
  *seed = iVar1;
  return;
}
