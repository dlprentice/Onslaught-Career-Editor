/* address: 0x0057ef10 */
/* name: CFastVB__Helper_0057ef10 */
/* signature: void __stdcall CFastVB__Helper_0057ef10(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Helper_0057ef10(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  uint *extraout_EAX;
  uint uVar4;
  uint *puVar5;
  uint uVar6;
  uint unaff_ESI;
  uint unaff_EDI;
  undefined2 in_FPUControlWord;
  undefined4 local_c;
  uint local_8;

  OID__AllocObject_DefaultTag_00662b2c(unaff_EDI << 4);
  if (extraout_EAX != (uint *)0x0) {
    fVar1 = (float)(int)unaff_ESI;
    if ((int)unaff_ESI < 0) {
      fVar1 = fVar1 + _DAT_005e72d8;
    }
    fVar2 = (float)(int)unaff_EDI;
    if ((int)unaff_EDI < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
    local_8 = 0;
    _DAT_009d0c54 = local_c;
    puVar5 = extraout_EAX;
    if (unaff_EDI != 0) {
      do {
        fVar3 = (float)(int)local_8;
        if ((int)local_8 < 0) {
          fVar3 = fVar3 + _DAT_005e72d8;
        }
        fVar3 = (fVar3 + _DAT_005e72d4) * (fVar1 / fVar2) + _DAT_005e72d4;
        uVar4 = (uint)ROUND(fVar3);
        uVar6 = uVar4 - 1;
        fVar3 = ((float)(int)uVar4 + _DAT_005e6a34) - fVar3;
        if ((int)uVar6 < 0) {
          uVar6 = -(uint)(param_1 != 0) & unaff_ESI - 1;
        }
        if (unaff_ESI <= uVar4) {
          uVar4 = ~-(uint)(param_1 != 0) & unaff_ESI - 1;
        }
        puVar5[1] = (uint)fVar3;
        *puVar5 = uVar6;
        puVar5[2] = uVar4;
        local_8 = local_8 + 1;
        puVar5[3] = (uint)(1.0 - fVar3);
        puVar5 = puVar5 + 4;
      } while (local_8 < unaff_EDI);
    }
  }
  return;
}
