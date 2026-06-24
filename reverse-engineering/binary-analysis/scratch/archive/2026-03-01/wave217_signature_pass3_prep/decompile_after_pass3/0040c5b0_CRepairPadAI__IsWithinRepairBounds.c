/* address: 0x0040c5b0 */
/* name: CRepairPadAI__IsWithinRepairBounds */
/* signature: int __thiscall CRepairPadAI__IsWithinRepairBounds(void * this) */


int __thiscall CRepairPadAI__IsWithinRepairBounds(void *this)

{
  if ((*(float *)(*(int *)((int)this + 0x4b0) + 0x20) <= *(float *)((int)this + 0xfc)) &&
     (*(float *)(*(int *)((int)this + 0x4b0) + 0x1c) <= *(float *)((int)this + 0xf8))) {
    return 1;
  }
  return 0;
}
