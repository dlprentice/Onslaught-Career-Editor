/* address: 0x00478160 */
/* name: CUnitAI__Unk_00478160 */
/* signature: int CUnitAI__Unk_00478160(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnitAI__Unk_00478160(void)

{
  float fVar1;
  float fVar2;
  float *pfVar3;
  float *pfVar4;
  float *pfVar5;
  float *pfVar6;
  uint uVar7;
  float *in_stack_00000004;
  float *in_stack_00000008;
  float *in_stack_0000000c;
  float *in_stack_00000010;
  float *in_stack_00000014;
  float *in_stack_00000018;
  float *in_stack_0000001c;
  uint local_4;

  pfVar6 = in_stack_0000001c;
  pfVar5 = in_stack_0000000c;
  pfVar4 = in_stack_00000008;
  pfVar3 = in_stack_00000004;
  uVar7 = 0;
  local_4 = 0;
  if (*in_stack_00000008 <= in_stack_0000001c[3]) {
    if (*in_stack_00000008 < in_stack_0000001c[1]) {
      local_4 = 2;
    }
  }
  else {
    local_4 = 1;
  }
  if (*in_stack_00000004 <= in_stack_0000001c[2]) {
    if (*in_stack_00000004 < *in_stack_0000001c) {
      local_4 = local_4 | 8;
    }
  }
  else {
    local_4 = local_4 | 4;
  }
  if (*in_stack_0000000c <= in_stack_0000001c[5]) {
    if (*in_stack_0000000c < in_stack_0000001c[4]) {
      local_4 = local_4 | 0x20;
    }
  }
  else {
    local_4 = local_4 | 0x10;
  }
  in_stack_00000004 = (float *)local_4;
  if (*in_stack_00000014 <= in_stack_0000001c[3]) {
    if (*in_stack_00000014 < in_stack_0000001c[1]) {
      uVar7 = 2;
    }
  }
  else {
    uVar7 = 1;
  }
  if (*in_stack_00000010 <= in_stack_0000001c[2]) {
    if (*in_stack_00000010 < *in_stack_0000001c) {
      uVar7 = uVar7 | 8;
    }
  }
  else {
    uVar7 = uVar7 | 4;
  }
  if (*in_stack_00000018 <= in_stack_0000001c[5]) {
    if (*in_stack_00000018 < in_stack_0000001c[4]) {
      uVar7 = uVar7 | 0x20;
    }
  }
  else {
    uVar7 = uVar7 | 0x10;
  }
  in_stack_0000000c = (float *)uVar7;
  if (uVar7 != 0 || local_4 != 0) {
    do {
      if (((uint)in_stack_00000004 & (uint)in_stack_0000000c) != 0) {
        return 0;
      }
      uVar7 = (uint)in_stack_0000000c;
      if (in_stack_00000004 != (float *)0x0) {
        uVar7 = (uint)in_stack_00000004;
      }
      if ((uVar7 & 1) == 0) {
        if ((uVar7 & 2) == 0) {
          if ((uVar7 & 4) == 0) {
            if ((uVar7 & 8) == 0) {
              if ((uVar7 & 0x10) == 0) {
                in_stack_0000001c = (float *)pfVar6[4];
                fVar2 = (pfVar6[4] - *pfVar5) / (*in_stack_00000018 - *pfVar5);
                fVar1 = (*in_stack_00000010 - *pfVar3) * fVar2 + *pfVar3;
                fVar2 = (*in_stack_00000014 - *pfVar4) * fVar2;
              }
              else {
                in_stack_0000001c = (float *)pfVar6[5];
                fVar2 = (pfVar6[5] - *pfVar5) / (*in_stack_00000018 - *pfVar5);
                fVar1 = (*in_stack_00000010 - *pfVar3) * fVar2 + *pfVar3;
                fVar2 = (*in_stack_00000014 - *pfVar4) * fVar2;
              }
              in_stack_00000008 = (float *)(fVar2 + *pfVar4);
              goto LAB_004783ce;
            }
            fVar1 = *pfVar6;
            fVar2 = *pfVar6;
          }
          else {
            fVar1 = pfVar6[2];
            fVar2 = pfVar6[2];
          }
          fVar2 = (fVar2 - *pfVar3) / (*in_stack_00000010 - *pfVar3);
          in_stack_00000008 = (float *)((*in_stack_00000014 - *pfVar4) * fVar2 + *pfVar4);
          in_stack_0000001c = (float *)((*in_stack_00000018 - *pfVar5) * fVar2 + *pfVar5);
        }
        else {
          fVar2 = (pfVar6[1] - *pfVar4) / (*in_stack_00000014 - *pfVar4);
          fVar1 = (*in_stack_00000010 - *pfVar3) * fVar2 + *pfVar3;
          in_stack_00000008 = (float *)pfVar6[1];
          in_stack_0000001c = (float *)((*in_stack_00000018 - *pfVar5) * fVar2 + *pfVar5);
        }
      }
      else {
        fVar2 = (pfVar6[3] - *pfVar4) / (*in_stack_00000014 - *pfVar4);
        fVar1 = (*in_stack_00000010 - *pfVar3) * fVar2 + *pfVar3;
        in_stack_00000008 = (float *)pfVar6[3];
        in_stack_0000001c = (float *)((*in_stack_00000018 - *pfVar5) * fVar2 + *pfVar5);
      }
LAB_004783ce:
      if ((float *)uVar7 == in_stack_00000004) {
        in_stack_00000004 = (float *)0x0;
        *pfVar3 = fVar1;
        *pfVar4 = (float)in_stack_00000008;
        *pfVar5 = (float)in_stack_0000001c;
        if (*pfVar4 <= pfVar6[3]) {
          if (*pfVar4 < pfVar6[1]) {
            in_stack_00000004 = (float *)0x2;
          }
        }
        else {
          in_stack_00000004 = (float *)0x1;
        }
        if (*pfVar3 <= pfVar6[2]) {
          if (*pfVar3 < *pfVar6) {
            in_stack_00000004 = (float *)((uint)in_stack_00000004 | 8);
          }
        }
        else {
          in_stack_00000004 = (float *)((uint)in_stack_00000004 | 4);
        }
        if ((float)in_stack_0000001c <= pfVar6[5]) {
          if ((float)in_stack_0000001c < pfVar6[4]) {
            in_stack_00000004 = (float *)((uint)in_stack_00000004 | 0x20);
          }
        }
        else {
          in_stack_00000004 = (float *)((uint)in_stack_00000004 | 0x10);
        }
      }
      else {
        *in_stack_00000010 = fVar1;
        *in_stack_00000014 = (float)in_stack_00000008;
        *in_stack_00000018 = (float)in_stack_0000001c;
        in_stack_0000000c = (float *)0x0;
        if (*in_stack_00000014 <= pfVar6[3]) {
          if (*in_stack_00000014 < pfVar6[1]) {
            in_stack_0000000c = (float *)0x2;
          }
        }
        else {
          in_stack_0000000c = (float *)0x1;
        }
        if (*in_stack_00000010 <= pfVar6[2]) {
          if (*in_stack_00000010 < *pfVar6) {
            in_stack_0000000c = (float *)((uint)in_stack_0000000c | 8);
          }
        }
        else {
          in_stack_0000000c = (float *)((uint)in_stack_0000000c | 4);
        }
        if ((float)in_stack_0000001c <= pfVar6[5]) {
          if ((float)in_stack_0000001c < pfVar6[4]) {
            in_stack_0000000c = (float *)((uint)in_stack_0000000c | 0x20);
          }
        }
        else {
          in_stack_0000000c = (float *)((uint)in_stack_0000000c | 0x10);
        }
      }
    } while (in_stack_0000000c != (float *)0x0 || in_stack_00000004 != (float *)0x0);
  }
  return 1;
}
