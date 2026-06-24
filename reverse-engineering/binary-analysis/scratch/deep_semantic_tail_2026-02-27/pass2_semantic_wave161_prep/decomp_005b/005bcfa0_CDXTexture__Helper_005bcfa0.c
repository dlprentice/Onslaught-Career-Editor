/* address: 0x005bcfa0 */
/* name: CDXTexture__Helper_005bcfa0 */
/* signature: int CDXTexture__Helper_005bcfa0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_005bcfa0(void)

{
  undefined4 *puVar1;
  undefined1 in_stack_00000004;
  undefined1 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;
  int in_stack_00000014;

  puVar1 = (undefined4 *)
           (**(code **)(in_stack_00000014 + 0x20))(*(undefined4 *)(in_stack_00000014 + 0x28),1,0x1c)
  ;
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = 0;
    *(undefined1 *)(puVar1 + 4) = in_stack_00000004;
    *(undefined1 *)((int)puVar1 + 0x11) = in_stack_00000008;
    puVar1[5] = in_stack_0000000c;
    puVar1[6] = in_stack_00000010;
  }
  return (int)puVar1;
}
