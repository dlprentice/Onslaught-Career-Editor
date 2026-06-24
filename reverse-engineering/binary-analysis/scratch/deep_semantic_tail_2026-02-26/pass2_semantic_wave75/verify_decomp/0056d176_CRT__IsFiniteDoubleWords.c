/* address: 0x0056d176 */
/* name: CRT__IsFiniteDoubleWords */
/* signature: bool __cdecl CRT__IsFiniteDoubleWords(int param_1, int param_2) */


bool __cdecl CRT__IsFiniteDoubleWords(int param_1,int param_2)

{
  return (param_2._2_2_ & 0x7ff0) != 0x7ff0;
}
