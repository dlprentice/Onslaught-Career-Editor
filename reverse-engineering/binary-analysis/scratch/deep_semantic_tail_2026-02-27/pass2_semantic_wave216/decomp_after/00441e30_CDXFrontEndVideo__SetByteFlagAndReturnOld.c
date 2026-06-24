/* address: 0x00441e30 */
/* name: CDXFrontEndVideo__SetByteFlagAndReturnOld */
/* signature: int __fastcall CDXFrontEndVideo__SetByteFlagAndReturnOld(void * param_1) */


int __fastcall CDXFrontEndVideo__SetByteFlagAndReturnOld(void *param_1)

{
  undefined1 uVar1;
  undefined4 in_EAX;

  uVar1 = *(undefined1 *)param_1;
  *(undefined1 *)param_1 = 1;
  return CONCAT31((int3)((uint)in_EAX >> 8),uVar1);
}
