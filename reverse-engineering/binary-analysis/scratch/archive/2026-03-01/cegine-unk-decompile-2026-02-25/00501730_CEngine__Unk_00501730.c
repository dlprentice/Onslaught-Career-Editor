/* address: 0x00501730 */
/* name: CEngine__Unk_00501730 */
/* signature: void CEngine__Unk_00501730(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_00501730(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  char *format;
  char acStack_100 [256];

  puVar1 = DAT_00854e68;
  puVar3 = DAT_00854e68;
  while (puVar2 = puVar1, DAT_00854e68 = puVar3, puVar2 != (undefined4 *)0x0) {
    puVar1 = (undefined4 *)puVar2[0x16];
    if ((puVar2[0xc] == 0) && (puVar2 != (undefined4 *)0x0)) {
      (**(code **)*puVar2)(1);
      puVar3 = DAT_00854e68;
    }
  }
  if (puVar3 == (undefined4 *)0x0) {
    format = s_No_shader_leaks_0063ce34;
  }
  else {
    DebugTrace(s__________________________________0063cee8);
    DebugTrace(s_Shader_leaks__I_ll_be_deleting_t_0063ceb4);
    DebugTrace(s__________________________________0063ce7c);
    do {
      sprintf(acStack_100,s_Shader___s__leaked__refcount__d_0063ce58);
      DebugTrace(acStack_100);
      puVar3 = (undefined4 *)puVar3[0x16];
    } while (puVar3 != (undefined4 *)0x0);
    format = s______________0063ce48;
  }
  DebugTrace(format);
  puVar1 = DAT_00854e68;
  while (puVar3 = puVar1, puVar3 != (undefined4 *)0x0) {
    puVar1 = (undefined4 *)puVar3[0x16];
    if (puVar3 != (undefined4 *)0x0) {
      (**(code **)*puVar3)(1);
    }
  }
  return;
}
