/* address: 0x004903a0 */
/* name: CDXEngine__Helper_004903a0 */
/* signature: void __thiscall CDXEngine__Helper_004903a0(void * this, int param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXEngine__Helper_004903a0(void *this,int param_1,int param_2,int param_3)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  float *pfVar5;
  float *pfVar6;
  float *pfVar7;
  double dVar8;

  pfVar1 = (float *)((int)this + param_1 * 0x74 + 0x1c4);
  pfVar5 = pfVar1 + 6;
  pfVar7 = (float *)((int)this + param_2 * 0x1c);
  pfVar6 = pfVar5;
  for (iVar4 = 0x17; iVar4 != 0; iVar4 = iVar4 + -1) {
    *pfVar6 = 0.0;
    pfVar6 = pfVar6 + 1;
  }
  pfVar1[7] = pfVar7[3];
  pfVar1[8] = pfVar7[4];
  dVar8 = CStaticShadows__Helper_0047eb80(0x6fadc8,pfVar7 + 3);
  fVar2 = (float)dVar8 - _DAT_005d85c0;
  if (pfVar7[5] <= fVar2) {
    fVar2 = pfVar7[5];
  }
  pfVar1[9] = fVar2;
  switch(pfVar7[1]) {
  case 0.0:
    fVar3 = *pfVar1 * _DAT_005dc238;
    *pfVar5 = 1.4013e-45;
    pfVar1[0xf] = 1.0;
    pfVar1[0x10] = 1.0;
    pfVar1[0x11] = 1.0;
    fVar2 = *pfVar7;
    pfVar1[1] = fVar3;
    pfVar1[0x12] = fVar2;
    pfVar1[3] = -0.1;
    pfVar1[4] = -0.1;
    pfVar1[5] = -0.1;
    pfVar1[2] = 1.4013e-44;
    break;
  case 1.4013e-45:
    fVar3 = *pfVar1 * _DAT_005dc234;
    *pfVar5 = 1.4013e-45;
    pfVar1[0xf] = 1.0;
    pfVar1[0x10] = 0.0;
    pfVar1[0x11] = 0.0;
    fVar2 = *pfVar7;
    pfVar1[1] = fVar3;
    fVar3 = _DAT_005d856c;
    pfVar1[0x12] = fVar2;
    pfVar1[2] = 7.00649e-45;
    pfVar1[4] = fVar3;
    pfVar1[5] = fVar3;
    pfVar1[3] = -0.2;
    break;
  case 2.8026e-45:
    fVar3 = *pfVar1 * _DAT_005dc234;
    *pfVar5 = 1.4013e-45;
    pfVar1[0xf] = 1.0;
    pfVar1[0x10] = 0.5;
    pfVar1[0x11] = 0.0;
    fVar2 = *pfVar7;
    pfVar1[2] = 7.00649e-45;
    pfVar1[1] = fVar3;
    pfVar1[0x12] = fVar2;
    pfVar1[3] = -0.2;
    pfVar1[4] = -0.1;
    pfVar1[5] = 0.0;
    break;
  case 4.2039e-45:
    fVar3 = *pfVar1 * _DAT_005dc234;
    pfVar1[0xf] = 1.0;
    pfVar1[0x10] = 1.0;
    *pfVar5 = 1.4013e-45;
    pfVar1[0x11] = 0.0;
    fVar2 = *pfVar7;
    pfVar1[1] = fVar3;
    pfVar1[0x12] = fVar2;
    pfVar1[2] = 7.00649e-45;
    pfVar1[3] = -0.2;
    pfVar1[4] = -0.2;
    pfVar1[5] = 0.0;
    break;
  case 5.60519e-45:
    fVar3 = *pfVar1 * _DAT_005dc234;
    *pfVar5 = 1.4013e-45;
    pfVar1[0xf] = 0.0;
    pfVar1[0x10] = 0.5;
    pfVar1[0x11] = 1.0;
    fVar2 = *pfVar7;
    pfVar1[2] = 7.00649e-45;
    pfVar1[1] = fVar3;
    pfVar1[0x12] = fVar2;
    pfVar1[3] = 0.0;
    pfVar1[4] = -0.1;
    pfVar1[5] = -0.2;
    break;
  default:
    goto switchD_00490416_default;
  }
  pfVar7 = (float *)(&DAT_009c65c0 + (param_1 + 2) * 0x17);
  for (iVar4 = 0x17; iVar4 != 0; iVar4 = iVar4 + -1) {
    *pfVar7 = *pfVar5;
    pfVar5 = pfVar5 + 1;
    pfVar7 = pfVar7 + 1;
  }
  (&DAT_009c68fe)[param_1] = 1;
  (&DAT_009c68a2)[param_1] = 1;
  (&DAT_009c6906)[param_1] = 1;
switchD_00490416_default:
  return;
}
