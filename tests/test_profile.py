"""
Module for testing profiles.
"""
from unittest import TestCase

from pabutools.election import (
    Instance,
    Project,
    ApprovalProfile,
    CardinalProfile,
    CumulativeProfile,
    OrdinalProfile,
    get_random_approval_profile,
    get_all_approval_profiles,
    ApprovalBallot,
    CardinalBallot,
    CumulativeBallot,
    OrdinalBallot,
    FrozenApprovalBallot,
    ApprovalMultiProfile,
    FrozenCardinalBallot,
    CardinalMultiProfile,
    FrozenCumulativeBallot,
    CumulativeMultiProfile,
    FrozenOrdinalBallot,
    OrdinalMultiProfile,
    Profile,
    Ballot,
    MultiProfile,
)
from tests.test_class_inheritence import check_members_equality


class TestProfile(TestCase):
    def test_profile(self):
        profile = Profile()
        b1 = ApprovalBallot()
        b2 = ApprovalBallot()
        b3 = ApprovalBallot()

        # Test general operations on profiles
        profile = profile.__add__(Profile([b1, b2]))
        assert len(profile) == 2
        profile *= 3
        assert len(profile) == 6
        profile.append(b3)
        assert len(profile) == 7
        profile.insert(1, b1)
        assert profile[1] == b1
        assert profile[2] == b2
        assert len(profile) == 8
        profile.__setitem__(0, b3)
        assert profile[0] == b3
        profile.extend(Profile([b1, b1]))
        assert len(profile) == 10
        assert profile[-1] == b1
        assert profile[-2] == b1
        profile.extend(
            (
                b2,
                b2,
            )
        )
        assert len(profile) == 12
        assert profile[-1] == b2
        assert profile[-2] == b2

        # Test constructor from another profile
        profile1 = Profile(
            instance=Instance([Project("qsd", 1)]),
            ballot_type=str,
            ballot_validation=False,
        )
        profile2 = Profile(profile1)
        check_members_equality(profile1, profile2)

    def test_multiprofile(self):
        profile = MultiProfile()
        b1 = FrozenApprovalBallot()
        b2 = FrozenApprovalBallot()
        b3 = FrozenApprovalBallot()

        profile.append(b1)
        profile.extend([b2, b3])

        # Test constructor from another profile
        profile1 = MultiProfile(
            instance=Instance([Project("qsd", 1)]),
            ballot_type=str,
            ballot_validation=False,
        )
        profile2 = MultiProfile(profile1)
        check_members_equality(profile1, profile2)

    def test_approval_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)

        b1 = ApprovalBallot((projects[0], projects[1]))
        b2 = ApprovalBallot((projects[2], projects[3]))
        b3 = ApprovalBallot((projects[4], projects[5]))

        # Test constructor
        profile = ApprovalProfile(
            [b1] * 5 + [b2] * 8 + [b3] * 5,
            instance=instance,
            legal_min_cost=2,
            legal_max_cost=9,
            legal_min_length=3,
            legal_max_length=10,
        )
        profile2 = ApprovalProfile(profile)
        check_members_equality(profile, profile2)

        # Test party list check
        profile = ApprovalProfile([b1] * 5 + [b2] * 8 + [b3] * 5, instance=instance)
        assert len(profile) == 18
        assert profile.is_party_list() is True
        b4 = ApprovalBallot([projects[0], projects[4]])
        profile.append(b4)
        assert profile.is_party_list() is False

        # Test other methods
        assert len(profile.approved_projects()) == 6
        assert profile.is_trivial() is True
        instance.budget_limit = 3
        assert profile.is_trivial() is False

        # Test ballot validation
        card_ballot = CardinalBallot({projects[1]: 5, projects[2]: 2})
        with self.assertRaises(TypeError):
            profile.append(card_ballot)
        with self.assertRaises(TypeError):
            ApprovalProfile([card_ballot])
        profile.ballot_validation = False
        profile.append(card_ballot)

        # Test random profile
        random_profile = get_random_approval_profile(instance, 10)
        assert len(random_profile) == 10

        # Test approval profiles generator
        new_inst = Instance(
            [Project("p1", 1), Project("p2", 1), Project("p3", 1)], budget_limit=3
        )
        assert len(list(get_all_approval_profiles(new_inst, 1))) == 8
        assert len(list(get_all_approval_profiles(new_inst, 2))) == 8 * 8
        assert len(list(get_all_approval_profiles(new_inst, 3))) == 8 * 8 * 8

    def test_app_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = FrozenApprovalBallot(projects[:4], name="name", meta={"metakey": 0})
        b2 = FrozenApprovalBallot(projects[1:6], name="name", meta={"metakey": 0})
        b3 = FrozenApprovalBallot({projects[0]}, name="name", meta={"metakey": 0})
        b4 = FrozenApprovalBallot(
            (projects[1], projects[4]), name="name", meta={"metakey": 0}
        )

        # Test that multiprofile behave as expected
        multiprofile = ApprovalMultiProfile((b1, b2, b3, b4))
        assert len(multiprofile) == 4
        assert multiprofile.total() == 4
        multiprofile.append(b1)
        assert len(multiprofile) == 4
        assert multiprofile.total() == 5

        # Test constructor from profile
        profile = ApprovalProfile(
            [ApprovalBallot(projects[:2])] * 4 + [ApprovalBallot(projects[:5])] * 10
        )
        assert len(profile) == 14
        multiprofile1 = ApprovalMultiProfile(profile=profile)
        assert len(multiprofile1) == 2
        assert multiprofile1.total() == 14
        multiprofile2 = profile.as_multiprofile()
        check_members_equality(multiprofile1, multiprofile2)
        assert len(multiprofile2) == 2
        assert multiprofile2.total() == 14

        # Test constructor from multiprofile
        m = ApprovalMultiProfile(multiprofile)
        check_members_equality(multiprofile, m)

        # Test empty constructor
        ApprovalMultiProfile()

    def test_cardinal_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(
            projects,
            budget_limit=1,
        )
        b1 = CardinalBallot(
            {
                projects[1]: 4,
                projects[2]: 74,
                projects[3]: 12,
                projects[4]: 7,
                projects[5]: -41,
            }
        )
        b2 = CardinalBallot(
            {
                projects[1]: 41,
                projects[2]: 4,
                projects[3]: 68,
                projects[4]: 7,
                projects[5]: 0,
            }
        )
        b3 = CardinalBallot(
            {
                projects[1]: 57,
                projects[2]: 5,
                projects[3]: 5857,
                projects[4]: 7786,
                projects[5]: -481,
            }
        )
        b4 = CardinalBallot(
            {
                projects[1]: 2,
                projects[2]: 8,
                projects[3]: 16872,
                projects[4]: 77,
                projects[5]: -457851,
            }
        )

        # General test
        profile = CardinalProfile(
            (b1, b2),
            instance=instance,
            legal_min_score=2,
            legal_max_score=9,
            legal_min_length=3,
            legal_max_length=10,
        )
        assert len(profile) == 2
        assert profile[0] == b1
        assert profile[1] == b2

        # Test constructor
        profile2 = CardinalProfile(profile)
        check_members_equality(profile, profile2)

        # Test ballot validation
        app_ballot = ApprovalBallot([projects[1], projects[2]])
        with self.assertRaises(TypeError):
            profile.append(app_ballot)
        with self.assertRaises(TypeError):
            CardinalProfile([app_ballot])
        profile.ballot_validation = False
        profile.append(app_ballot)

        # Test completion method
        profile = CardinalProfile((b1, b2))
        assert len(set(p for b in profile for p in b)) == 5
        profile.complete(projects, 0.2)
        assert len(set(p for b in profile for p in b)) == 10

    def test_card_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = FrozenCardinalBallot({projects[1]: 8}, name="name", meta={"metakey": 0})
        b2 = FrozenCardinalBallot({projects[0]: 10}, name="name", meta={"metakey": 0})
        b3 = FrozenCardinalBallot(
            {projects[i]: i for i in range(len(projects))},
            name="name",
            meta={"metakey": 0},
        )
        b4 = FrozenCardinalBallot(
            {projects[3]: 1, projects[1]: 4}, name="name", meta={"metakey": 0}
        )

        # Test that multiprofile behave as expected
        multiprofile = CardinalMultiProfile((b1, b2, b3, b4))
        assert len(multiprofile) == 4
        assert multiprofile.total() == 4
        multiprofile.append(b1)
        assert len(multiprofile) == 4
        assert multiprofile.total() == 5

        # Test constructor from profile
        profile = CardinalProfile(
            [CardinalBallot({projects[2]: 5})] * 4
            + [CardinalBallot({projects[5]: 8})] * 10
        )
        assert len(profile) == 14
        multiprofile1 = CardinalMultiProfile(profile=profile)
        assert len(multiprofile1) == 2
        assert multiprofile1.total() == 14
        multiprofile2 = profile.as_multiprofile()
        check_members_equality(multiprofile1, multiprofile2)
        assert len(multiprofile2) == 2
        assert multiprofile2.total() == 14

        # Test constructor from multiprofile
        m = CardinalMultiProfile(multiprofile)
        check_members_equality(multiprofile, m)

        # Test empty constructor
        CardinalMultiProfile()

    def test_cumulative_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = CumulativeBallot(
            {
                projects[1]: 4,
                projects[2]: 74,
                projects[3]: 12,
                projects[4]: 7,
                projects[5]: -41,
            }
        )
        b2 = CumulativeBallot(
            {
                projects[1]: 41,
                projects[2]: 4,
                projects[3]: 68,
                projects[4]: 7,
                projects[5]: 0,
            }
        )
        b3 = CumulativeBallot(
            {
                projects[1]: 57,
                projects[2]: 5,
                projects[3]: 5857,
                projects[4]: 7786,
                projects[5]: -481,
            }
        )
        b4 = CumulativeBallot(
            {
                projects[1]: 2,
                projects[2]: 8,
                projects[3]: 16872,
                projects[4]: 77,
                projects[5]: -457851,
            }
        )

        # General test
        profile = CumulativeProfile(
            (b1, b2, b3),
            instance=instance,
            legal_min_score=2,
            legal_max_score=9,
            legal_min_length=3,
            legal_max_length=10,
            legal_min_total_score=0,
            legal_max_total_score=24,
        )
        assert len(profile) == 3
        assert profile[0] == b1
        assert profile[1] == b2
        assert profile[2] == b3

        # Test constructor
        profile2 = CumulativeProfile(profile)
        check_members_equality(profile, profile2)

        # Test ballot validation
        app_ballot = ApprovalBallot([projects[0], projects[2]])
        with self.assertRaises(TypeError):
            profile.append(app_ballot)
        with self.assertRaises(TypeError):
            CumulativeProfile([app_ballot])
        profile.ballot_validation = False
        profile.append(app_ballot)

        # Test completion method
        profile = CumulativeProfile((b1, b2))
        assert len(set(p for b in profile for p in b)) == 5
        profile.complete(projects, 0.2)
        assert len(set(p for b in profile for p in b)) == 10

    def test_cum_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = FrozenCumulativeBallot({projects[1]: 8}, name="name", meta={"metakey": 0})
        b2 = FrozenCumulativeBallot({projects[0]: 10}, name="name", meta={"metakey": 0})
        b3 = FrozenCumulativeBallot(
            {projects[i]: i for i in range(len(projects))},
            name="name",
            meta={"metakey": 0},
        )
        b4 = FrozenCumulativeBallot(
            {projects[3]: 1, projects[1]: 4}, name="name", meta={"metakey": 0}
        )

        # Test that multiprofile behave as expected
        multiprofile = CumulativeMultiProfile((b1, b2, b3, b4))
        assert len(multiprofile) == 4
        assert multiprofile.total() == 4
        multiprofile.append(b1)
        assert len(multiprofile) == 4
        assert multiprofile.total() == 5

        # Test constructor from profile
        profile = CumulativeProfile(
            [CumulativeBallot({projects[2]: 25})] * 4
            + [CumulativeBallot({projects[5]: 8})] * 10
        )
        assert len(profile) == 14
        multiprofile1 = CumulativeMultiProfile(profile=profile)
        assert len(multiprofile1) == 2
        assert multiprofile1.total() == 14
        multiprofile2 = profile.as_multiprofile()
        check_members_equality(multiprofile1, multiprofile2)
        assert len(multiprofile2) == 2
        assert multiprofile2.total() == 14

        # Test constructor from multiprofile
        m = CumulativeMultiProfile(multiprofile)
        check_members_equality(multiprofile, m)

        # Test empty constructor
        CumulativeMultiProfile()

    def test_ordinal_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        b2 = OrdinalBallot([projects[4], projects[5], projects[3]])
        b3 = OrdinalBallot([projects[2], projects[3], projects[7]])

        # General test
        profile = OrdinalProfile(
            (b1, b2, b3), instance=instance, legal_min_length=1, legal_max_length=423
        )
        assert len(profile) == 3

        # Test constructor
        profile2 = OrdinalProfile(profile)
        check_members_equality(profile, profile2)

        # Test ballot validation
        app_ballot = ApprovalBallot([projects[0], projects[2]])
        with self.assertRaises(TypeError):
            profile.append(app_ballot)
        with self.assertRaises(TypeError):
            OrdinalProfile([app_ballot])
        profile.ballot_validation = False
        profile.append(app_ballot)

    def test_ord_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = FrozenOrdinalBallot(projects[1:8], name="name", meta={"metakey": 0})
        b2 = FrozenOrdinalBallot(projects[:-1], name="name", meta={"metakey": 0})
        b3 = FrozenOrdinalBallot(
            {projects[1], projects[4]}, name="name", meta={"metakey": 0}
        )
        b4 = FrozenOrdinalBallot(tuple(projects), name="name", meta={"metakey": 0})

        # Test that multiprofile behave as expected
        multiprofile = OrdinalMultiProfile((b1, b2, b3, b4))
        assert len(multiprofile) == 4
        assert multiprofile.total() == 4
        multiprofile.append(b1)
        assert len(multiprofile) == 4
        assert multiprofile.total() == 5

        # Test constructor from profile
        profile = OrdinalProfile(
            [OrdinalBallot(set(projects))] * 4
            + [OrdinalBallot([projects[5], projects[0]])] * 10
        )
        assert len(profile) == 14
        multiprofile1 = OrdinalMultiProfile(profile=profile)
        assert len(multiprofile1) == 2
        assert multiprofile1.total() == 14
        multiprofile2 = profile.as_multiprofile()
        check_members_equality(multiprofile1, multiprofile2)
        assert len(multiprofile2) == 2
        assert multiprofile2.total() == 14

        # Test constructor from multiprofile
        m = OrdinalMultiProfile(multiprofile)
        check_members_equality(multiprofile, m)

        # Test empty constructor
        OrdinalMultiProfile()
