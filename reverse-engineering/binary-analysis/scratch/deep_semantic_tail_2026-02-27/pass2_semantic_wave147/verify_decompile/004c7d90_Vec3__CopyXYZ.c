/* address: 0x004c7d90 */
/* name: Vec3__CopyXYZ */
/* signature: void __thiscall Vec3__CopyXYZ(void * this, void * param_1, void * param_2) */


void __thiscall Vec3__CopyXYZ(void *this,void *param_1,void *param_2)

{
  *(undefined4 *)this = *(undefined4 *)param_1;
  *(undefined4 *)((int)this + 4) = *(undefined4 *)((int)param_1 + 4);
  *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)param_1 + 8);
  return;
}
