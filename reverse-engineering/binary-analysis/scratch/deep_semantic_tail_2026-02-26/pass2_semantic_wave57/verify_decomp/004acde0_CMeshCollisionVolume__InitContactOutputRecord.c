/* address: 0x004acde0 */
/* name: CMeshCollisionVolume__InitContactOutputRecord */
/* signature: undefined CMeshCollisionVolume__InitContactOutputRecord(void) */


void CMeshCollisionVolume__InitContactOutputRecord(void)

{
  undefined4 *unaff_EBX;
  undefined4 in_stack_00000020;
  undefined4 in_stack_00000040;
  undefined4 in_stack_00000044;
  undefined4 in_stack_00000048;
  undefined4 in_stack_0000004c;

  unaff_EBX[4] = in_stack_00000040;
  unaff_EBX[5] = in_stack_00000044;
  unaff_EBX[6] = in_stack_00000048;
  unaff_EBX[7] = in_stack_0000004c;
  *unaff_EBX = 0;
  unaff_EBX[1] = 0;
  unaff_EBX[2] = 0;
  unaff_EBX[3] = in_stack_00000020;
  unaff_EBX[8] = 1;
  return;
}
