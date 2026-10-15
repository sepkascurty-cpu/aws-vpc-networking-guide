# VPC Networking Quiz

5 questions. Try them cold, then expand the answers.

---

### 1. Your EC2 in a public subnet has a public IP, but SSH times out. The security group allows port 22 from your IP. What else could block it?

<details>
<summary>Answer</summary>

The **route table** (no `0.0.0.0/0 → igw` route — it's not really a public subnet), the **network ACL** (inbound rule missing, or the *ephemeral port* range blocked on outbound — NACLs are stateless, so return traffic needs its own rule), or the instance's own OS firewall. Check in this order: route table → NACL → SG → OS.
</details>

### 2. Security group vs network ACL: which one can explicitly DENY traffic?

<details>
<summary>Answer</summary>

The **network ACL**. Security groups only have *allow* rules (everything else is implicitly denied); NACLs support explicit allow **and** deny rules, evaluated in numbered order — first match wins. That's why a NACL is the right tool for blocking a known-bad IP range subnet-wide.
</details>

### 3. Your private EC2 can `ping 8.8.8.8` but can't reach S3. The NAT Gateway is healthy. What broke — and what's the free fix?

<details>
<summary>Answer</summary>

Nothing "broke" — traffic to S3 leaves through the NAT Gateway, which works, but **S3 bucket policies** often restrict access to VPC endpoints, or you're paying NAT data-processing charges unnecessarily. The free fix: add a **Gateway Endpoint for S3** to the private route table. It routes S3 traffic privately inside AWS, costs nothing, and keeps it off the public internet.
</details>

### 4. Why should each AZ have its own NAT Gateway instead of sharing one?

<details>
<summary>Answer</summary>

A NAT Gateway lives in a single AZ. If that AZ goes down, every private subnet routing through it loses egress — you've traded a regional design for a **single point of failure**. One NAT GW per AZ keeps failures isolated. (Cost-saving exception: dev/test VPCs often run one NAT GW and accept the risk — a deliberate trade-off, not an accident.)
</details>

### 5. You launch an RDS instance into a private subnet but your app still can't connect. Name two networking-layer causes.

<details>
<summary>Answer</summary>

1. **Security group**: the RDS SG must allow inbound on the DB port (e.g. 5432/3306) from the app tier's security group — the default SG allows nothing inbound.
2. **Subnet group / NACL**: RDS must sit in a DB subnet group spanning ≥2 AZs, and the subnet's NACL must allow the DB port inbound *and* the ephemeral ports outbound (stateless!). A third classic: the app and RDS are in different VPCs with no peering.

---

Scored 4–5? You're ready to design a VPC from memory. 2–3? Re-read the SG-vs-NACL table in the README. 0–1? Run `subnet_planner.py` and build one in the console — muscle memory beats flashcards. 💪
