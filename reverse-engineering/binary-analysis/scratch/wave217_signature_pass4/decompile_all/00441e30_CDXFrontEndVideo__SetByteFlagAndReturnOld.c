/* address: 0x00441e30 */
/* name: CDXFrontEndVideo__SetByteFlagAndReturnOld */
/* signature: int __thiscall CDXFrontEndVideo__SetByteFlagAndReturnOld(void * this) */


int __thiscall CDXFrontEndVideo__SetByteFlagAndReturnOld(void *this)

{
  undefined1 uVar1;
  undefined4 in_EAX;

  uVar1 = *(undefined1 *)this;
  *(undefined1 *)this = 1;
  return CONCAT31((int3)((uint)in_EAX >> 8),uVar1);
}
