/* address: 0x004e0b30 */
/* name: CSoundManager__PlaySample */
/* signature: int CSoundManager__PlaySample(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CSoundManager__PlaySample(void)

{
  float fVar1;
  int *piVar2;
  undefined4 in_EAX;
  int iVar3;
  int in_ECX;
  int in_stack_00000004;
  int in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;
  char in_stack_00000014;
  undefined4 in_stack_00000018;
  undefined4 in_stack_0000001c;
  undefined4 in_stack_00000020;
  undefined4 in_stack_00000024;
  undefined4 in_stack_00000028;
  undefined4 in_stack_0000002c;
  undefined4 in_stack_00000030;
  undefined4 in_stack_00000034;

  iVar3 = CONCAT31((int3)((uint)in_EAX >> 8),*(char *)(in_ECX + 4));
  if (*(char *)(in_ECX + 4) != '\0') {
    fVar1 = *(float *)(in_ECX + 0x20);
    iVar3 = CONCAT22((short)((uint)in_EAX >> 0x10),
                     (ushort)(fVar1 < _DAT_005d856c) << 8 |
                     (ushort)(NAN(fVar1) || NAN(_DAT_005d856c)) << 10 |
                     (ushort)(fVar1 == _DAT_005d856c) << 0xe);
    if (((fVar1 == _DAT_005d856c) == 0) &&
       ((DAT_008a9ac0 != 1 || (iVar3 = 1, (char)in_stack_00000024 != '\0')))) {
      if (in_stack_00000014 != '\0') {
        for (piVar2 = *(int **)(in_ECX + 0xc); piVar2 != (int *)0x0; piVar2 = (int *)piVar2[0x1d]) {
          if (((char)piVar2[2] != '\0') && (piVar2[3] == in_stack_00000004)) {
            if (*piVar2 == 0) {
              return (int)piVar2;
            }
            if (*piVar2 == in_stack_00000008) {
              return (int)piVar2;
            }
          }
        }
      }
      iVar3 = CSoundManager__PlaySound
                        (in_stack_00000008,in_stack_00000004,in_stack_00000010,in_stack_0000000c,
                         in_stack_00000018,in_stack_0000001c,in_stack_00000020,in_stack_00000024,
                         in_stack_00000028,in_stack_0000002c,in_stack_00000030,in_stack_00000034);
    }
  }
  return iVar3;
}
