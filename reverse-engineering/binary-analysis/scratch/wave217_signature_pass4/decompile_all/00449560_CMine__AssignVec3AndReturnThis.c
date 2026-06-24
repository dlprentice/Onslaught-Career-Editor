/* address: 0x00449560 */
/* name: CMine__AssignVec3AndReturnThis */
/* signature: void * __thiscall CMine__AssignVec3AndReturnThis(void * this, int x_bits, int y_bits, int z_bits) */


void * __thiscall CMine__AssignVec3AndReturnThis(void *this,int x_bits,int y_bits,int z_bits)

{
  *(undefined4 *)this = *(undefined4 *)x_bits;
  *(undefined4 *)((int)this + 4) = *(undefined4 *)y_bits;
  *(undefined4 *)((int)this + 8) = *(undefined4 *)z_bits;
  return this;
}
