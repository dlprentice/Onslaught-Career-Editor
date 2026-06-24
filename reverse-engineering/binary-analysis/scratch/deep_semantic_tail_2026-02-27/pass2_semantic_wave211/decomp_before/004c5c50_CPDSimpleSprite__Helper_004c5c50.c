/* address: 0x004c5c50 */
/* name: CPDSimpleSprite__Helper_004c5c50 */
/* signature: void __fastcall CPDSimpleSprite__Helper_004c5c50(float param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CPDSimpleSprite__Helper_004c5c50(float param_1)

{
  float fVar1;
  float *pfVar2;
  float fVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;

  iVar7 = 0;
  fVar3 = param_1;
  fVar1 = param_1;
  do {
    uVar6 = 0;
    pfVar2 = (float *)(&DAT_00829e58 + iVar7 * 0x40);
    do {
      switch(iVar7) {
      case 0:
        fVar3 = 2.24208e-44;
        param_1 = 5.60519e-45;
        fVar1 = _DAT_005dbb50;
        break;
      case 1:
        fVar3 = 1.12104e-44;
        param_1 = 4.2039e-45;
        fVar1 = _DAT_005d8c4c;
        break;
      case 2:
        fVar3 = 5.60519e-45;
        param_1 = 2.8026e-45;
        fVar1 = _DAT_005d858c;
        break;
      case 3:
        fVar3 = 2.8026e-45;
        param_1 = 1.4013e-45;
        fVar1 = _DAT_005d85ec;
        break;
      case 4:
        fVar3 = 1.4013e-45;
        param_1 = 0.0;
        fVar1 = _DAT_005d8568;
      }
      uVar4 = (int)fVar3 - 1U & uVar6;
      iVar5 = (int)uVar6 >> (SUB41(param_1,0) & 0x1f);
      uVar6 = uVar6 + 1;
      *pfVar2 = (float)(int)uVar4 * fVar1;
      pfVar2[1] = (float)iVar5 * fVar1;
      pfVar2[2] = fVar1 + *pfVar2;
      pfVar2[3] = fVar1 + pfVar2[1];
      pfVar2 = pfVar2 + 4;
    } while ((int)uVar6 < 0x10);
    iVar7 = iVar7 + 1;
  } while (iVar7 < 5);
  DAT_0082b39c = 1;
  return;
}
